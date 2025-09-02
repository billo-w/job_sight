from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Configure application logging with multiple levels"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Use a simpler format that works better with syslog/Better Stack
    # The log level will be properly transmitted via syslog priority
    log_format = '%(message)s'
    
    # Clear any existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('job_sight.log', mode='a')
        ],
        force=True  # Force reconfiguration
    )
    
    # Create application logger
    logger = logging.getLogger('job_sight')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Set specific log levels for different components
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask request logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)   # Reduce HTTP request logs
    
    return logger

# Setup logging
logger = setup_logging()

# Create Flask app
app = Flask(__name__)

# Add startup logging with proper levels
logger.info("Starting Job Sight application...")
logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'unknown')}")
logger.info(f"Log level set to: {os.environ.get('LOG_LEVEL', 'INFO')}")
if os.environ.get('DATABASE_URL'):
    logger.info(f"Database URL configured: {os.environ.get('DATABASE_URL', 'not set')[:20]}...")
else:
    logger.warning("DATABASE_URL not configured, using default SQLite")

# IP Restriction functionality
def check_ip_restriction():
    """Check if IP restrictions are enabled and if current IP is allowed"""
    if not os.environ.get('ENABLE_IP_RESTRICTIONS', 'false').lower() == 'true':
        return True  # No restrictions enabled
    
    allowed_ips = os.environ.get('ALLOWED_IPS', '').split(',')
    if not allowed_ips or allowed_ips == ['']:
        return True  # No IPs specified, allow all
    
    client_ip = request.remote_addr
    # Check if client IP is in allowed list
    for allowed_ip in allowed_ips:
        allowed_ip = allowed_ip.strip()
        if allowed_ip == client_ip or allowed_ip == '0.0.0.0/0':
            return True
        # Simple CIDR check (for basic ranges like 192.168.1.0/24)
        if '/' in allowed_ip:
            try:
                import ipaddress
                if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_ip):
                    return True
            except:
                pass
    
    return False

@app.before_request
def before_request():
    """Check IP restrictions before processing any request"""
    # Skip IP restriction check for health endpoint
    if request.endpoint == 'health_check':
        return
    
    if not check_ip_restriction():
        client_ip = request.remote_addr
        logger.warning(f"Access denied for IP {client_ip} - not in allowed list")
        return jsonify({'error': 'Access denied. Your IP is not authorized to access this environment.'}), 403

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///job_sight.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    saved_jobs = db.relationship('SavedJob', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    salary_min = db.Column(db.Numeric(10, 2), nullable=True)
    salary_max = db.Column(db.Numeric(10, 2), nullable=True)
    job_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simple API Services
class JobAPI:
    def __init__(self):
        self.app_id = os.environ.get('ADZUNA_APP_ID')
        self.app_key = os.environ.get('ADZUNA_APP_KEY')
        self.base_url = 'https://api.adzuna.com/v1/api/jobs'

    def search_jobs(self, job_title, location, page=1):
        if not all([self.app_id, self.app_key]):
            logger.error("Adzuna API credentials not configured - missing app_id or app_key")
            return {'error': 'API credentials not configured', 'results': [], 'count': 0}

        logger.info(f"Searching jobs: '{job_title}' in '{location}' (page {page})")
        
        try:
            url = f"{self.base_url}/gb/search/{page}"
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': job_title,
                'where': location,
                'results_per_page': 20,
                'sort_by': 'relevance'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            job_count = data.get('count', 0)
            logger.info(f"Successfully fetched {job_count} jobs from Adzuna API")
            
            formatted_jobs = []
            for job in data.get('results', []):
                formatted_job = {
                    'id': job.get('id', ''),
                    'title': job.get('title', 'No title'),
                    'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                    'location': job.get('location', {}).get('display_name', 'Unknown Location'),
                    'description': job.get('description', 'No description'),
                    'salary_min': job.get('salary_min'),
                    'salary_max': job.get('salary_max'),
                    'redirect_url': job.get('redirect_url', ''),
                    'created': job.get('created', '')
                }
                formatted_jobs.append(formatted_job)
            
            return {
                'results': formatted_jobs,
                'count': job_count,
                'page': page,
                'total_pages': (job_count + 19) // 20
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error when fetching jobs for '{job_title}' in '{location}'")
            return {'error': 'Request timeout - please try again', 'results': [], 'count': 0}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} when fetching jobs: {str(e)}")
            return {'error': f'API error: {e.response.status_code}', 'results': [], 'count': 0}
        except Exception as e:
            logger.error(f"Unexpected error in job search: {str(e)}", exc_info=True)
            return {'error': f'Failed to fetch jobs: {str(e)}', 'results': [], 'count': 0}

class AIService:
    def __init__(self):
        self.endpoint = os.environ.get('AZURE_AI_ENDPOINT')
        self.api_key = os.environ.get('AZURE_AI_KEY')

    def generate_summary(self, job_title, location, job_results):
        if not all([self.endpoint, self.api_key]):
            logger.warning("Azure AI service not configured - missing endpoint or API key")
            return {'summary': 'AI service not configured', 'error': True}

        logger.info(f"Generating AI summary for '{job_title}' in '{location}' with {len(job_results)} jobs")
        
        try:
            # Prepare job data for AI
            companies = list(set([job.get('company', '') for job in job_results[:10] if job.get('company')]))
            salary_data = [job for job in job_results if job.get('salary_min') or job.get('salary_max')]
            
            if salary_data:
                avg_min = sum(job.get('salary_min', 0) for job in salary_data) / len(salary_data)
                avg_max = sum(job.get('salary_max', 0) for job in salary_data) / len(salary_data)
                salary_info = f"Average salary range: £{avg_min:,.0f} - £{avg_max:,.0f}"
            else:
                salary_info = "Salary information not available"

            prompt = f"""
            Analyze the job market for "{job_title}" positions in "{location}":
            
            Total jobs found: {len(job_results)}
            Top companies: {', '.join(companies[:5]) if companies else 'Various companies'}
            {salary_info}
            
            Provide a concise market summary covering:
            1. Market demand and competition level
            2. Salary expectations
            3. Key insights for recruiters
            
            Keep response under 300 words.
            """

            payload = {
                "messages": [
                    {"role": "system", "content": "You are a recruitment analyst providing market insights."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.7
            }

            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }

            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            summary = result['choices'][0]['message']['content'].strip()
            logger.info("Successfully generated AI summary")
            return {'summary': summary, 'error': False}
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error when generating AI summary for '{job_title}' in '{location}'")
            return {'summary': 'AI service timeout - please try again', 'error': True}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} when calling Azure AI: {str(e)}")
            return {'summary': 'AI service temporarily unavailable', 'error': True}
        except Exception as e:
            logger.error(f"Unexpected error in AI summary generation: {str(e)}", exc_info=True)
            return {'summary': 'Unable to generate summary at this time.', 'error': True}

# Routes
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection using proper SQLAlchemy syntax
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy', 
        'message': 'Job Sight application is running',
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'database': db_status,
        'ip_restrictions': os.environ.get('ENABLE_IP_RESTRICTIONS', 'false')
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        location = request.form.get('location', '').strip()
        page = request.args.get('page', 1, type=int)
        
        if not job_title or not location:
            flash('Please enter both job title and location', 'error')
            return render_template('index.html')
        
        # Search for jobs
        job_api = JobAPI()
        search_results = job_api.search_jobs(job_title, location, page)
        
        # Generate AI summary
        ai_summary = None
        if search_results.get('results') and not search_results.get('error'):
            ai_service = AIService()
            ai_summary = ai_service.generate_summary(job_title, location, search_results['results'])
        
        return render_template('results.html',
                             search_results=search_results,
                             ai_summary=ai_summary,
                             job_title=job_title,
                             location=location,
                             page=page)
    
    # Handle GET requests (for popular search links)
    job_title = request.args.get('job_title', '').strip()
    location = request.args.get('location', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if job_title and location:
        # Search for jobs
        job_api = JobAPI()
        search_results = job_api.search_jobs(job_title, location, page)
        
        # Generate AI summary
        ai_summary = None
        if search_results.get('results') and not search_results.get('error'):
            ai_service = AIService()
            ai_summary = ai_service.generate_summary(job_title, location, search_results['results'])
        
        return render_template('results.html',
                             search_results=search_results,
                             ai_summary=ai_summary,
                             job_title=job_title,
                             location=location,
                             page=page)
    
    return render_template('index.html')

@app.route('/save_job', methods=['POST'])
@login_required
def save_job():
    try:
        job_data = request.get_json()
        
        # Check if job already saved
        existing_job = SavedJob.query.filter_by(
            user_id=current_user.id,
            job_id=job_data['job_id']
        ).first()
        
        if existing_job:
            logger.debug(f"User {current_user.username} attempted to save already saved job {job_data['job_id']}")
            return jsonify({'success': False, 'message': 'Job already saved'})
        
        # Save new job
        saved_job = SavedJob(
            user_id=current_user.id,
            job_id=job_data['job_id'],
            job_title=job_data['job_title'],
            company=job_data['company'],
            location=job_data['location'],
            salary_min=job_data.get('salary_min'),
            salary_max=job_data.get('salary_max'),
            job_url=job_data['job_url'],
            description=job_data.get('description', '')
        )
        
        db.session.add(saved_job)
        db.session.commit()
        
        logger.info(f"User {current_user.username} saved job: {job_data['job_title']} at {job_data['company']}")
        return jsonify({'success': True, 'message': 'Job saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save job for user {current_user.username}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Failed to save job'})

@app.route('/unsave_job', methods=['POST'])
@login_required
def unsave_job():
    try:
        job_data = request.get_json()
        saved_job = SavedJob.query.filter_by(
            user_id=current_user.id,
            job_id=job_data['job_id']
        ).first()
        
        if saved_job:
            job_title = saved_job.job_title
            company = saved_job.company
            db.session.delete(saved_job)
            db.session.commit()
            logger.info(f"User {current_user.username} removed saved job: {job_title} at {company}")
            return jsonify({'success': True, 'message': 'Job removed from saved jobs'})
        else:
            logger.debug(f"User {current_user.username} attempted to remove non-existent saved job {job_data['job_id']}")
            return jsonify({'success': False, 'message': 'Job not found in saved jobs'})
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to remove saved job for user {current_user.username}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Failed to remove job'})

@app.route('/saved_jobs')
@login_required
def saved_jobs():
    page = request.args.get('page', 1, type=int)
    saved_jobs = SavedJob.query.filter_by(user_id=current_user.id)\
                              .order_by(SavedJob.saved_at.desc())\
                              .paginate(page=page, per_page=20, error_out=False)
    return render_template('saved_jobs.html', saved_jobs=saved_jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        # Basic validation
        if not all([username, email, first_name, last_name, password, password2]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != password2:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {username} ({email})")
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration failed for user {username}: {str(e)}", exc_info=True)
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or next_page.startswith('/'):
                next_page = url_for('index')
            logger.info(f"User {username} logged in successfully")
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    saved_jobs_count = SavedJob.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', saved_jobs_count=saved_jobs_count)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error: {request.url} not found")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Could not create database tables: {e}", exc_info=True)
            logger.warning("Continuing without database initialization...")
    
    logger.info("Job Sight application startup complete")
    app.run(debug=False, port=5000)
