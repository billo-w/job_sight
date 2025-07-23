import pytest
import tempfile
import os
from app import create_app
from models import db, User, SavedJob, SearchHistory


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'ADZUNA_APP_ID': 'test-app-id',
        'ADZUNA_APP_KEY': 'test-app-key',
        'AZURE_AI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_AI_KEY': 'test-azure-key',
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


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
def authenticated_client(client, test_user):
    """A client with an authenticated user."""
    client.post('/login', data={
        'username': test_user.username,
        'password': 'testpassword123'
    })
    return client


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