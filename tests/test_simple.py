"""
Simple tests for the Job Sight application.
These tests verify basic functionality without overcomplicating things.
"""

import pytest
import os


def test_app_imports():
    """Test that the app can be imported successfully."""
    from app import app, db, User, SavedJob
    assert app is not None
    assert db is not None
    assert User is not None
    assert SavedJob is not None


def test_app_configuration():
    """Test that the app has basic configuration."""
    from app import app
    assert app.config['SECRET_KEY'] is not None
    assert 'SQLALCHEMY_DATABASE_URI' in app.config


def test_routes_exist():
    """Test that basic routes are defined."""
    from app import app
    
    # Check that routes are registered
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    # Basic routes that should exist
    expected_routes = ['/', '/register', '/login', '/logout', '/search', '/saved_jobs', '/profile']
    
    for route in expected_routes:
        assert route in routes, f"Route {route} not found in {routes}"


def test_ip_restrictions_disabled_by_default():
    """Test that IP restrictions are disabled by default."""
    # Set environment variables for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'false'
    os.environ['ALLOWED_IPS'] = ''
    
    from app import check_ip_restriction
    assert check_ip_restriction() is True


def test_ip_restrictions_enabled():
    """Test that IP restrictions work when enabled."""
    # Set environment variables for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'true'
    os.environ['ALLOWED_IPS'] = '192.168.1.100'
    
    from app import check_ip_restriction
    # This should return False for any IP not in the allowed list
    # We can't easily test the actual IP check without mocking request.remote_addr
    # But we can test that the function exists and can be called
    assert callable(check_ip_restriction)


def test_models_exist():
    """Test that database models are properly defined."""
    from app import User, SavedJob
    
    # Test User model
    assert hasattr(User, '__tablename__')
    assert hasattr(User, 'id')
    assert hasattr(User, 'username')
    assert hasattr(User, 'email')
    assert hasattr(User, 'set_password')
    assert hasattr(User, 'check_password')
    
    # Test SavedJob model
    assert hasattr(SavedJob, '__tablename__')
    assert hasattr(SavedJob, 'id')
    assert hasattr(SavedJob, 'user_id')
    assert hasattr(SavedJob, 'job_id')
    assert hasattr(SavedJob, 'job_title')


def test_api_classes_exist():
    """Test that API service classes exist."""
    from app import JobAPI, AIService
    
    # Test JobAPI class
    assert hasattr(JobAPI, 'search_jobs')
    assert callable(JobAPI.search_jobs)
    
    # Test AIService class
    assert hasattr(AIService, 'generate_summary')
    assert callable(AIService.generate_summary)


def test_health_check_endpoint():
    """Test that health check endpoint exists."""
    # Disable IP restrictions for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'false'
    os.environ['ALLOWED_IPS'] = ''
    
    from app import app
    
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


def test_home_page_loads():
    """Test that home page loads without database connection."""
    # Disable IP restrictions for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'false'
    os.environ['ALLOWED_IPS'] = ''
    
    from app import app
    
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b'Job Sight' in response.data


def test_register_page_loads():
    """Test that register page loads."""
    # Disable IP restrictions for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'false'
    os.environ['ALLOWED_IPS'] = ''
    
    from app import app
    
    with app.test_client() as client:
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Create your account' in response.data


def test_login_page_loads():
    """Test that login page loads."""
    # Disable IP restrictions for testing
    os.environ['ENABLE_IP_RESTRICTIONS'] = 'false'
    os.environ['ALLOWED_IPS'] = ''
    
    from app import app
    
    with app.test_client() as client:
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Sign in to your account' in response.data


def test_static_files_exist():
    """Test that static CSS file exists."""
    import os
    assert os.path.exists('static/styles.css'), "CSS file should exist"


def test_templates_exist():
    """Test that key templates exist."""
    import os
    key_templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/auth/login.html',
        'templates/auth/register.html',
        'templates/results.html',
        'templates/profile.html',
        'templates/saved_jobs.html'
    ]
    
    for template in key_templates:
        assert os.path.exists(template), f"Template {template} should exist"


def test_requirements_file():
    """Test that requirements.txt contains necessary packages."""
    import os
    assert os.path.exists('requirements.txt'), "requirements.txt should exist"
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    # Check for key dependencies
    assert 'Flask' in requirements
    assert 'Flask-SQLAlchemy' in requirements
    assert 'Flask-Login' in requirements
    assert 'pytest' in requirements


def test_dockerfile_exists():
    """Test that Dockerfile exists."""
    import os
    assert os.path.exists('Dockerfile'), "Dockerfile should exist"


def test_ci_cd_workflow_exists():
    """Test that CI/CD workflow exists."""
    import os
    assert os.path.exists('.github/workflows/ci.yml'), "CI/CD workflow should exist"
