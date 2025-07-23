import pytest
from flask import url_for
from models import db, User


class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_register_get(self, client):
        """Test GET request to register page."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
        assert b'Username' in response.data
        assert b'Email' in response.data
        assert b'Password' in response.data
    
    def test_register_post_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='johndoe').first()
            assert user is not None
            assert user.email == 'john@example.com'
            assert user.first_name == 'John'
            assert user.last_name == 'Doe'
            assert user.check_password('password123')
    
    def test_register_post_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': test_user.username,  # Duplicate username
            'email': 'jane@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_register_post_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith',
            'email': test_user.email,  # Duplicate email
            'password': 'password123',
            'password2': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_register_post_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith',
            'email': 'jane@example.com',
            'password': 'password123',
            'password2': 'differentpassword'
        })
        
        assert response.status_code == 200
        assert b'Passwords must match' in response.data
    
    def test_register_post_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith',
            'email': 'invalid-email',
            'password': 'password123',
            'password2': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Please enter a valid email address' in response.data
    
    def test_register_post_short_password(self, client):
        """Test registration with password too short."""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith',
            'email': 'jane@example.com',
            'password': 'short',
            'password2': 'short'
        })
        
        assert response.status_code == 200
        assert b'Password must be at least 8 characters' in response.data
    
    def test_register_redirect_if_authenticated(self, authenticated_client):
        """Test that authenticated users are redirected from register page."""
        response = authenticated_client.get('/register', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to home page
        assert b'Job Search' in response.data or b'Search Jobs' in response.data
    
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'Sign In' in response.data
        assert b'Username' in response.data
        assert b'Password' in response.data
    
    def test_login_post_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'username': test_user.username,
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert f'Welcome back, {test_user.first_name}!'.encode() in response.data
    
    def test_login_post_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post('/login', data={
            'username': 'nonexistentuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_post_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        response = client.post('/login', data={
            'username': test_user.username,
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_post_empty_fields(self, client):
        """Test login with empty fields."""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })
        
        assert response.status_code == 200
        # Should show validation errors
        assert b'This field is required' in response.data or b'required' in response.data.lower()
    
    def test_login_redirect_if_authenticated(self, authenticated_client):
        """Test that authenticated users are redirected from login page."""
        response = authenticated_client.get('/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to home page
        assert b'Job Search' in response.data or b'Search Jobs' in response.data
    
    def test_login_with_next_parameter(self, client, test_user):
        """Test login with next parameter for redirection."""
        # Try to access a protected page
        response = client.get('/profile')
        assert response.status_code == 302  # Redirect to login
        
        # Login with next parameter
        response = client.post('/login?next=/profile', data={
            'username': test_user.username,
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should be redirected to the profile page
        assert b'Profile' in response.data or b'Recent Searches' in response.data
    
    def test_logout(self, authenticated_client):
        """Test user logout."""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data
        
        # Verify user is logged out by trying to access protected page
        response = authenticated_client.get('/profile')
        assert response.status_code == 302  # Should redirect to login
    
    def test_logout_requires_authentication(self, client):
        """Test that logout requires authentication."""
        response = client.get('/logout')
        assert response.status_code == 302  # Should redirect to login
    
    def test_profile_requires_authentication(self, client):
        """Test that profile page requires authentication."""
        response = client.get('/profile')
        assert response.status_code == 302  # Should redirect to login
    
    def test_profile_authenticated_access(self, authenticated_client, test_user):
        """Test authenticated access to profile page."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        assert test_user.first_name.encode() in response.data
        assert b'Profile' in response.data or b'Recent Searches' in response.data
    
    def test_saved_jobs_requires_authentication(self, client):
        """Test that saved jobs page requires authentication."""
        response = client.get('/saved_jobs')
        assert response.status_code == 302  # Should redirect to login
    
    def test_saved_jobs_authenticated_access(self, authenticated_client):
        """Test authenticated access to saved jobs page."""
        response = authenticated_client.get('/saved_jobs')
        assert response.status_code == 200
        assert b'Saved Jobs' in response.data