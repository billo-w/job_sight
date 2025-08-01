import pytest
import tempfile
import os
from flask import Flask
from models import db, User, SavedJob, SearchHistory
from tests.config import TestConfig


@pytest.fixture
def app():
    """Create a simple test app."""
    test_config = TestConfig()
    
    try:
        app = Flask(__name__)
        app.config.from_object(test_config)
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    finally:
        test_config.cleanup()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_saved_job(app, test_user):
    """Create a test saved job."""
    with app.app_context():
        saved_job = SavedJob(
            user_id=test_user.id,
            job_id='test-job-123',
            job_title='Software Engineer',
            company='Test Company',
            location='London',
            salary_min=50000,
            salary_max=70000,
            job_url='https://example.com/job/123',
            description='Test job description'
        )
        db.session.add(saved_job)
        db.session.commit()
        return saved_job


@pytest.fixture
def test_search_history(app, test_user):
    """Create test search history."""
    with app.app_context():
        search = SearchHistory(
            user_id=test_user.id,
            job_title='Python Developer',
            location='Manchester',
            results_count=25
        )
        db.session.add(search)
        db.session.commit()
        return search