from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.urls import url_parse
import logging
from datetime import datetime

# Import local modules
from config import Config
from models import db, User, SavedJob, SearchHistory
from forms import RegistrationForm, LoginForm, JobSearchForm, SaveJobForm
from services.adzuna_api import AdzunaAPI
from services.azure_ai import AzureAIService

def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add built-in functions to Jinja2 environment
    app.jinja_env.globals.update(min=min, max=max)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    return app

app = create_app()

# Routes
@app.route('/')
def index():
    """Home page with job search form."""
    form = JobSearchForm()
    return render_template('index.html', form=form)

@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    """Search for jobs using Adzuna API and display results with AI summary."""
    form = JobSearchForm()
    
    if form.validate_on_submit():
        job_title = form.job_title.data.strip()
        location = form.location.data.strip()
        page = request.args.get('page', 1, type=int)
        
        # Initialize services
        adzuna_api = AdzunaAPI()
        azure_ai = AzureAIService()
        
        # Search for jobs
        search_results = adzuna_api.search_jobs(
            job_title=job_title,
            location=location,
            page=page,
            results_per_page=app.config['JOBS_PER_PAGE']
        )
        
        # Generate AI summary if we have results
        ai_summary = None
        if search_results.get('results') and not search_results.get('error'):
            ai_summary = azure_ai.generate_job_market_summary(
                job_title=job_title,
                location=location,
                job_results=search_results['results']
            )
        
        # Save search history for logged-in users
        if current_user.is_authenticated:
            try:
                search_history = SearchHistory(
                    user_id=current_user.id,
                    job_title=job_title,
                    location=location,
                    results_count=search_results.get('count', 0)
                )
                db.session.add(search_history)
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Failed to save search history: {str(e)}")
                db.session.rollback()
        
        return render_template('results.html',
                             form=form,
                             search_results=search_results,
                             ai_summary=ai_summary,
                             job_title=job_title,
                             location=location,
                             page=page)
    
    # If form validation fails, redirect back to home
    return render_template('index.html', form=form)

@app.route('/save_job', methods=['POST'])
@login_required
def save_job():
    """Save a job for the current user."""
    try:
        job_data = request.get_json()
        
        # Check if job is already saved
        existing_job = SavedJob.query.filter_by(
            user_id=current_user.id,
            job_id=job_data['job_id']
        ).first()
        
        if existing_job:
            return jsonify({'success': False, 'message': 'Job already saved'})
        
        # Create new saved job
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
        
        return jsonify({'success': True, 'message': 'Job saved successfully'})
        
    except Exception as e:
        app.logger.error(f"Failed to save job: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to save job'})

@app.route('/unsave_job', methods=['POST'])
@login_required
def unsave_job():
    """Remove a saved job for the current user."""
    try:
        job_data = request.get_json()
        
        saved_job = SavedJob.query.filter_by(
            user_id=current_user.id,
            job_id=job_data['job_id']
        ).first()
        
        if saved_job:
            db.session.delete(saved_job)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Job removed from saved jobs'})
        else:
            return jsonify({'success': False, 'message': 'Job not found in saved jobs'})
            
    except Exception as e:
        app.logger.error(f"Failed to unsave job: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to remove job'})

@app.route('/saved_jobs')
@login_required
def saved_jobs():
    """Display user's saved jobs."""
    page = request.args.get('page', 1, type=int)
    
    saved_jobs = SavedJob.query.filter_by(user_id=current_user.id)\
                              .order_by(SavedJob.saved_at.desc())\
                              .paginate(
                                  page=page,
                                  per_page=app.config['JOBS_PER_PAGE'],
                                  error_out=False
                              )
    
    return render_template('saved_jobs.html', saved_jobs=saved_jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            app.logger.error(f"Registration failed: {str(e)}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    # Get user's recent search history
    recent_searches = SearchHistory.query.filter_by(user_id=current_user.id)\
                                        .order_by(SearchHistory.search_date.desc())\
                                        .limit(10).all()
    
    # Get saved jobs count
    saved_jobs_count = SavedJob.query.filter_by(user_id=current_user.id).count()
    
    return render_template('profile.html',
                         recent_searches=recent_searches,
                         saved_jobs_count=saved_jobs_count)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=5000)