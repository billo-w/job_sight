# Import Flask core components for web application functionality
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
# Import Flask-Login components for user session management and authentication
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# Import Flask-Migrate for database schema version control and migrations
from flask_migrate import Migrate
# Import Flask-CORS for cross-origin resource sharing
from flask_cors import CORS
# Import Flask-Limiter for rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Import URL parsing utilities for secure redirect validation
from urllib.parse import urlsplit
# Import logging module for application monitoring and debugging
import logging
import structlog
from pythonjsonlogger import jsonlogger
# Import datetime for timestamp operations
from datetime import datetime
import time
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Import local application modules
from config import Config  # Application configuration class
from models import db, User, SavedJob, SearchHistory  # Database models and SQLAlchemy instance
from forms import RegistrationForm, LoginForm, JobSearchForm, SaveJobForm  # WTForms form classes
from services.adzuna_api import AdzunaAPI  # External job search API service
from services.azure_ai import AzureAIService  # Azure AI integration for job market analysis

# Initialize Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
JOB_SEARCHES = Counter('job_searches_total', 'Total job searches', ['location', 'job_title'])
API_CALLS = Counter('api_calls_total', 'Total API calls', ['service', 'status'])
DATABASE_OPERATIONS = Counter('database_operations_total', 'Database operations', ['operation', 'table'])

def setup_logging():
    """Configure structured logging for production monitoring"""
    # Configure structlog for structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add JSON formatter for structured logging
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s'
    ))
    root_logger.addHandler(json_handler)

def create_app():
    """
    Application factory pattern implementation for Flask.
    This pattern allows for better testing, configuration management, and deployment flexibility.
    Returns a configured Flask application instance with all extensions initialized.
    """
    # Setup structured logging
    setup_logging()
    
    # Create Flask application instance with current module name
    app = Flask(__name__)
    
    # Load configuration from Config class - centralizes all app settings
    app.config.from_object(Config)
    
    # Initialize Flask-CORS for cross-origin resource sharing
    # Allow all origins for monitoring endpoints to ensure dashboard works
    CORS(app, resources={
        r"/health": {"origins": "*"},
        r"/metrics": {"origins": "*"}
    })
    
    # Initialize Flask-Limiter for rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Initialize SQLAlchemy database extension with the app instance
    # This creates the database connection pool and ORM functionality
    db.init_app(app)
    
    # Initialize Flask-Migrate for database schema version control
    # Enables database migrations for schema changes in production
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login extension for user session management
    login_manager = LoginManager()
    # Bind the login manager to the Flask application
    login_manager.init_app(app)
    # Set the login view route for redirecting unauthenticated users
    login_manager.login_view = 'login'
    # Set flash message for login requirement
    login_manager.login_message = 'Please log in to access this page.'
    # Set flash message category for styling purposes
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        User loader callback for Flask-Login.
        This function is called to reload the user object from the user ID stored in the session.
        Required by Flask-Login to manage user sessions across requests.
        """
        # Query database for user by ID and return User object or None
        return User.query.get(int(user_id))
    
    # Add Python built-in functions to Jinja2 template environment
    # This allows templates to use min() and max() functions directly
    app.jinja_env.globals.update(min=min, max=max)
    
    # Request monitoring middleware
    @app.before_request
    def before_request():
        """Log request details and start timing"""
        request.start_time = time.time()
        app.logger.info(f"Request started - {request.method} {request.path} from {request.remote_addr}")

    @app.after_request
    def after_request(response):
        """Log response details, record metrics, and add security headers"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            REQUEST_LATENCY.observe(duration)
            
            # Record request metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()
            
            app.logger.info(f"Request completed - {request.method} {request.path} {response.status_code} ({duration:.3f}s)")
        
        # Add security headers (CSP temporarily disabled for development)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; font-src 'self' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; img-src 'self' data: https:; connect-src 'self' https://cdn.tailwindcss.com;"
        
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors with logging"""
        app.logger.warning(f"Page not found - {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors with logging and database rollback"""
        app.logger.error(f"Internal server error - {str(error)} on {request.path}")
        db.session.rollback()
        return render_template('500.html'), 500

    # Health check endpoint for monitoring
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring systems"""
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            app.logger.error(f"Database health check failed: {str(e)}")
            db_status = 'unhealthy'
        
        # Test external API connections
        try:
            adzuna_api = AdzunaAPI()
            adzuna_status = 'healthy'
        except Exception as e:
            app.logger.error(f"Adzuna API health check failed: {str(e)}")
            adzuna_status = 'unhealthy'
        
        health_status = {
            'status': 'healthy' if all([db_status == 'healthy', adzuna_status == 'healthy']) else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db_status,
                'adzuna_api': adzuna_status
            },
            'version': os.getenv('APP_VERSION', '1.0.0')
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code

    # Metrics endpoint for Prometheus
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    # Define application routes using Flask decorators
    
    @app.route('/')
    def index():
        """
        Home page route handler.
        Displays the main job search interface with an empty search form.
        This is the application entry point for users.
        """
        # Create an instance of the job search form for the template
        form = JobSearchForm()
        # Render the home page template with the search form
        return render_template('index.html', form=form)

    @app.route('/search', methods=['GET', 'POST'])
    def search_jobs():
        """
        Job search route handler supporting both GET and POST methods.
        Processes job search requests, integrates with Adzuna API,
        generates AI summaries, and saves search history for authenticated users.
        """
        # Create form instance for validation and data extraction
        form = JobSearchForm()
        
        # Check if form was submitted and passes validation
        if form.validate_on_submit():
            # Extract and clean form data to prevent injection attacks
            job_title = form.job_title.data.strip()
            location = form.location.data.strip()
            # Get pagination parameter from URL query string, default to page 1
            page = request.args.get('page', 1, type=int)
            
            # Record job search metrics
            JOB_SEARCHES.labels(
                location=location,
                job_title=job_title
            ).inc()
            
            app.logger.info(f"Job search initiated - job_title: {job_title}, location: {location}, page: {page}, user_id: {current_user.id if current_user.is_authenticated else None}")
            
            # Initialize external service instances for API calls
            adzuna_api = AdzunaAPI()  # Job search API service
            azure_ai = AzureAIService()  # AI analysis service
            
            # Call Adzuna API to search for jobs with user parameters
            try:
                search_results = adzuna_api.search_jobs(
                    job_title=job_title,
                    location=location,
                    page=page,
                    results_per_page=app.config['JOBS_PER_PAGE']  # Pagination limit from config
                )
                API_CALLS.labels(service='adzuna', status='success').inc()
                app.logger.info(f"Adzuna API call successful - job_title: {job_title}, location: {location}, results_count: {search_results.get('count', 0)}")
            except Exception as e:
                API_CALLS.labels(service='adzuna', status='error').inc()
                app.logger.error(f"Adzuna API call failed - error: {str(e)}, job_title: {job_title}, location: {location}")
                search_results = {'error': 'Failed to fetch jobs', 'results': []}
            
            # Initialize AI summary variable
            ai_summary = None
            # Generate AI market analysis if search returned valid results
            if search_results.get('results') and not search_results.get('error'):
                try:
                    # Call Azure AI service to analyze job market trends
                    ai_summary = azure_ai.generate_job_market_summary(
                        job_title=job_title,
                        location=location,
                        job_results=search_results['results']
                    )
                    API_CALLS.labels(service='azure_ai', status='success').inc()
                    app.logger.info(f"Azure AI analysis completed - job_title: {job_title}, location: {location}")
                except Exception as e:
                    API_CALLS.labels(service='azure_ai', status='error').inc()
                    app.logger.error(f"Azure AI analysis failed - error: {str(e)}, job_title: {job_title}, location: {location}")
            
            # Save search history for authenticated users only
            if current_user.is_authenticated:
                try:
                    # Create new search history record
                    search_history = SearchHistory(
                        user_id=current_user.id,  # Link to current user
                        job_title=job_title,
                        location=location,
                        results_count=search_results.get('count', 0)  # Number of results found
                    )
                    # Add record to database session
                    db.session.add(search_history)
                    # Commit transaction to persist data
                    db.session.commit()
                    DATABASE_OPERATIONS.labels(operation='insert', table='search_history').inc()
                    app.logger.info(f"Search history saved - user_id: {current_user.id}, job_title: {job_title}, location: {location}")
                except Exception as e:
                    # Log error for debugging and monitoring
                    app.logger.error(f"Failed to save search history - error: {str(e)}, user_id: {current_user.id}")
                    # Rollback transaction to maintain database consistency
                    db.session.rollback()
            
            # Render results page with search data and AI analysis
            return render_template('results.html',
                                 form=form,
                                 search_results=search_results,
                                 ai_summary=ai_summary,
                                 job_title=job_title,
                                 location=location,
                                 page=page)
        
        # If form validation fails, redirect back to home page with form errors
        return render_template('index.html', form=form)

    @app.route('/save_job', methods=['POST'])
    @login_required  # Decorator ensures only authenticated users can access this route
    def save_job():
        """
        AJAX endpoint for saving jobs to user's saved jobs list.
        Accepts JSON data, validates job doesn't already exist,
        and creates new SavedJob record in database.
        """
        try:
            # Extract JSON data from POST request body
            job_data = request.get_json()
            
            app.logger.info("Job save attempt",
                           user_id=current_user.id,
                           job_id=job_data.get('job_id'),
                           job_title=job_data.get('job_title'),
                           company=job_data.get('company'))
            
            # Check if job is already saved by this user to prevent duplicates
            existing_job = SavedJob.query.filter_by(
                user_id=current_user.id,
                job_id=job_data['job_id']
            ).first()
            
            # Return error response if job already exists
            if existing_job:
                app.logger.info("Job already saved",
                               user_id=current_user.id,
                               job_id=job_data['job_id'])
                return jsonify({'success': False, 'message': 'Job already saved'})
            
            # Create new SavedJob instance with job data
            saved_job = SavedJob(
                user_id=current_user.id,  # Link to current authenticated user
                job_id=job_data['job_id'],  # External job ID from Adzuna
                job_title=job_data['job_title'],
                company=job_data['company'],
                location=job_data['location'],
                salary_min=job_data.get('salary_min'),  # Optional field
                salary_max=job_data.get('salary_max'),  # Optional field
                job_url=job_data['job_url'],
                description=job_data.get('description', '')  # Default to empty string
            )
            
            # Add new record to database session
            db.session.add(saved_job)
            # Commit transaction to persist the saved job
            db.session.commit()
            
            # Record database operation metric
            DATABASE_OPERATIONS.labels(operation='insert', table='saved_jobs').inc()
            
            app.logger.info("Job saved successfully",
                           user_id=current_user.id,
                           job_id=job_data['job_id'],
                           job_title=job_data['job_title'])
            
            # Return success response for AJAX call
            return jsonify({'success': True, 'message': 'Job saved successfully'})
            
        except Exception as e:
            # Log error for debugging and monitoring
            app.logger.error(f"Failed to save job: {str(e)}")
            # Rollback transaction to maintain database consistency
            db.session.rollback()
            # Return error response to client
            return jsonify({'success': False, 'message': 'Failed to save job'})

    @app.route('/unsave_job', methods=['POST'])
    @login_required  # Decorator ensures only authenticated users can access this route
    def unsave_job():
        """
        AJAX endpoint for removing jobs from user's saved jobs list.
        Accepts JSON data with job_id and removes corresponding SavedJob record.
        """
        try:
            # Extract JSON data from POST request body
            job_data = request.get_json()
            
            # Find the saved job record for this user and job ID
            saved_job = SavedJob.query.filter_by(
                user_id=current_user.id,
                job_id=job_data['job_id']
            ).first()
            
            # If job exists in saved jobs, delete it
            if saved_job:
                # Remove record from database session
                db.session.delete(saved_job)
                # Commit transaction to persist the deletion
                db.session.commit()
                # Return success response
                return jsonify({'success': True, 'message': 'Job removed from saved jobs'})
            else:
                # Return error if job not found in saved jobs
                return jsonify({'success': False, 'message': 'Job not found in saved jobs'})
                
        except Exception as e:
            # Log error for debugging and monitoring
            app.logger.error(f"Failed to unsave job: {str(e)}")
            # Rollback transaction to maintain database consistency
            db.session.rollback()
            # Return error response to client
            return jsonify({'success': False, 'message': 'Failed to remove job'})

    @app.route('/saved_jobs')
    @login_required  # Decorator ensures only authenticated users can access this route
    def saved_jobs():
        """
        Display user's saved jobs with pagination.
        Queries SavedJob records for current user and implements pagination
        for better performance with large datasets.
        """
        # Get page number from URL query string, default to page 1
        page = request.args.get('page', 1, type=int)
        
        # Query saved jobs for current user with pagination
        saved_jobs = SavedJob.query.filter_by(user_id=current_user.id)\
                                  .order_by(SavedJob.saved_at.desc())\
                                  .paginate(
                                      page=page,  # Current page number
                                      per_page=app.config['JOBS_PER_PAGE'],  # Items per page from config
                                      error_out=False  # Don't raise 404 for invalid page numbers
                                  )
        
        # Render saved jobs template with paginated results
        return render_template('saved_jobs.html', saved_jobs=saved_jobs)

    @app.route('/register', methods=['GET', 'POST'])
    @limiter.limit("3 per minute")
    def register():
        """
        User registration route handler.
        Displays registration form and processes new user creation
        with password hashing and database persistence.
        """
        # Redirect authenticated users away from registration page
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        # Create registration form instance
        form = RegistrationForm()
        
        # Process form submission if validation passes
        if form.validate_on_submit():
            try:
                # Create new User instance with form data
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data
                )
                # Hash and set password using Werkzeug security functions
                user.set_password(form.password.data)
                
                # Add new user to database session
                db.session.add(user)
                # Commit transaction to persist the new user
                db.session.commit()
                
                # Flash success message for user feedback
                flash('Registration successful! You can now log in.', 'success')
                # Redirect to login page after successful registration
                return redirect(url_for('login'))
                
            except Exception as e:
                # Log registration error for debugging
                app.logger.error(f"Registration failed: {str(e)}")
                # Rollback transaction to maintain database consistency
                db.session.rollback()
                # Flash error message to user
                flash('Registration failed. Please try again.', 'error')
        
        # Render registration template with form (includes validation errors)
        return render_template('auth/register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def login():
        """
        User login route handler.
        Authenticates users, manages sessions, and handles secure redirects
        to prevent open redirect vulnerabilities.
        """
        # Redirect authenticated users away from login page
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        # Create login form instance
        form = LoginForm()
        
        # Process form submission if validation passes
        if form.validate_on_submit():
            # Query database for user by username
            user = User.query.filter_by(username=form.username.data).first()
            
            # Verify user exists and password is correct
            if user and user.check_password(form.password.data):
                # Log user in using Flask-Login (creates session)
                login_user(user)
                
                # Handle secure redirect to prevent open redirect attacks
                next_page = request.args.get('next')
                # Validate redirect URL to prevent external redirects
                if not next_page or urlsplit(next_page).netloc != '':
                    next_page = url_for('index')
                
                # Flash welcome message with user's first name
                flash(f'Welcome back, {user.first_name}!', 'success')
                # Redirect to intended page or home
                return redirect(next_page)
            else:
                # Flash error message for invalid credentials
                flash('Invalid username or password', 'error')
        
        # Render login template with form (includes validation errors)
        return render_template('auth/login.html', form=form)

    @app.route('/logout')
    @login_required  # Decorator ensures only authenticated users can logout
    def logout():
        """
        User logout route handler.
        Clears user session and redirects to home page.
        """
        # Clear user session using Flask-Login
        logout_user()
        # Flash logout confirmation message
        flash('You have been logged out.', 'info')
        # Redirect to home page
        return redirect(url_for('index'))

    @app.route('/profile')
    @login_required  # Decorator ensures only authenticated users can access profile
    def profile():
        """
        User profile page route handler.
        Displays user information, recent search history, and saved jobs statistics.
        """
        # Query user's recent search history with limit for performance
        recent_searches = SearchHistory.query.filter_by(user_id=current_user.id)\
                                            .order_by(SearchHistory.search_date.desc())\
                                            .limit(10).all()
        
        # Count total saved jobs for user statistics
        saved_jobs_count = SavedJob.query.filter_by(user_id=current_user.id).count()
        
        # Render profile template with user data
        return render_template('profile.html',
                             recent_searches=recent_searches,
                             saved_jobs_count=saved_jobs_count)
    
    # Return configured Flask application instance
    return app

# Create application instance using factory pattern
# This allows for easy testing and configuration management
app = create_app()

# Application entry point for direct execution
if __name__ == '__main__':
    # Create application context for database operations
    with app.app_context():
        # Create all database tables if they don't exist
        db.create_all()
    # Run Flask development server on port 5000
    # Debug disabled for production-like behavior
    app.run(debug=False, port=5000)