import pytest
from models import db, User


class TestAuthRoutes:
    """Simple tests for authentication functionality."""
    
    def test_user_registration(self, app):
        """Test user registration functionality."""
        with app.app_context():
            # Test creating a user
            user = User(
                username='newuser',
                email='newuser@example.com',
                first_name='New',
                last_name='User'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            created_user = User.query.filter_by(username='newuser').first()
            assert created_user is not None
            assert created_user.email == 'newuser@example.com'
            assert created_user.check_password('password123')
    
    def test_user_login_validation(self, app, test_user):
        """Test user login validation."""
        with app.app_context():
            # Test correct password
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.check_password('testpassword123')
            
            # Test incorrect password
            assert not user.check_password('wrongpassword')
    
    def test_duplicate_username_prevention(self, app, test_user):
        """Test that duplicate usernames are prevented."""
        with app.app_context():
            # Try to create user with same username
            duplicate_user = User(
                username='testuser',  # Same as test_user
                email='different@example.com',
                first_name='Different',
                last_name='User'
            )
            duplicate_user.set_password('password123')
            
            db.session.add(duplicate_user)
            
            # Should raise an integrity error
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_duplicate_email_prevention(self, app, test_user):
        """Test that duplicate emails are prevented."""
        with app.app_context():
            # Try to create user with same email
            duplicate_user = User(
                username='differentuser',
                email='test@example.com',  # Same as test_user
                first_name='Different',
                last_name='User'
            )
            duplicate_user.set_password('password123')
            
            db.session.add(duplicate_user)
            
            # Should raise an integrity error
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_password_hashing(self, app):
        """Test password hashing functionality."""
        with app.app_context():
            user = User(
                username='hashtest',
                email='hash@example.com',
                first_name='Hash',
                last_name='Test'
            )
            password = 'mysecretpassword'
            user.set_password(password)
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != password
            assert user.password_hash is not None
            
            # Should be able to verify correct password
            assert user.check_password(password) is True
            
            # Should reject incorrect password
            assert user.check_password('wrongpassword') is False