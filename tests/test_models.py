import pytest
from datetime import datetime
from models import db, User, SavedJob, SearchHistory


class TestUser:
    """Test cases for the User model."""
    
    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                username='newuser',
                email='newuser@example.com',
                first_name='New',
                last_name='User'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.first_name == 'New'
            assert user.last_name == 'User'
            assert user.created_at is not None
            assert user.updated_at is not None
    
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
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
    
    def test_get_full_name(self, app):
        """Test getting user's full name."""
        with app.app_context():
            user = User(
                username='testuser2',
                email='test2@example.com',
                first_name='Test',
                last_name='User'
            )
            assert user.get_full_name() == 'Test User'
    
    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                username='testuser3',
                email='test3@example.com',
                first_name='Test',
                last_name='User'
            )
            assert repr(user) == '<User testuser3>'


class TestSavedJob:
    """Test cases for the SavedJob model."""
    
    def test_saved_job_creation(self, app):
        """Test creating a saved job."""
        with app.app_context():
            # Create user first
            user = User(
                username='jobuser',
                email='jobuser@example.com',
                first_name='Job',
                last_name='User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            saved_job = SavedJob(
                user_id=user.id,
                job_id='unique-job-123',
                job_title='Senior Developer',
                company='Amazing Company',
                location='Manchester',
                salary_min=60000,
                salary_max=80000,
                job_url='https://example.com/job/123',
                description='Great job opportunity'
            )
            
            db.session.add(saved_job)
            db.session.commit()
            
            assert saved_job.id is not None
            assert saved_job.user_id == user.id
            assert saved_job.job_id == 'unique-job-123'
            assert saved_job.job_title == 'Senior Developer'
            assert saved_job.company == 'Amazing Company'
            assert saved_job.location == 'Manchester'
            assert saved_job.salary_min == 60000
            assert saved_job.salary_max == 80000
            assert saved_job.job_url == 'https://example.com/job/123'
            assert saved_job.description == 'Great job opportunity'
            assert saved_job.saved_at is not None
    
    def test_get_salary_range(self, app):
        """Test salary range formatting."""
        with app.app_context():
            # Test with both min and max salary
            job1 = SavedJob(
                user_id=1,  # Use dummy user_id for testing
                job_id='job1',
                job_title='Job 1',
                company='Company',
                location='Location',
                salary_min=50000,
                salary_max=70000,
                job_url='https://example.com'
            )
            assert job1.get_salary_range() == '£50,000 - £70,000'
            
            # Test with only min salary
            job2 = SavedJob(
                user_id=1,
                job_id='job2',
                job_title='Job 2',
                company='Company',
                location='Location',
                salary_min=45000,
                job_url='https://example.com'
            )
            assert job2.get_salary_range() == '£45,000+'
            
            # Test with only max salary
            job3 = SavedJob(
                user_id=1,
                job_id='job3',
                job_title='Job 3',
                company='Company',
                location='Location',
                salary_max=60000,
                job_url='https://example.com'
            )
            assert job3.get_salary_range() == 'Up to £60,000'
            
            # Test with no salary
            job4 = SavedJob(
                user_id=1,
                job_id='job4',
                job_title='Job 4',
                company='Company',
                location='Location',
                job_url='https://example.com'
            )
            assert job4.get_salary_range() == 'Salary not specified'
    
    def test_saved_job_repr(self, app):
        """Test saved job string representation."""
        with app.app_context():
            saved_job = SavedJob(
                user_id=1,
                job_id='test-job-123',
                job_title='Software Engineer',
                company='Test Company',
                location='London',
                job_url='https://example.com/job/123'
            )
            assert repr(saved_job) == '<SavedJob Software Engineer at Test Company>'


class TestSearchHistory:
    """Test cases for the SearchHistory model."""
    
    def test_search_history_creation(self, app):
        """Test creating search history."""
        with app.app_context():
            # Create user first
            user = User(
                username='searchuser',
                email='searchuser@example.com',
                first_name='Search',
                last_name='User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            search = SearchHistory(
                user_id=user.id,
                job_title='Data Scientist',
                location='Birmingham',
                results_count=15
            )
            
            db.session.add(search)
            db.session.commit()
            
            assert search.id is not None
            assert search.user_id == user.id
            assert search.job_title == 'Data Scientist'
            assert search.location == 'Birmingham'
            assert search.results_count == 15
            assert search.search_date is not None
    
    def test_search_history_repr(self, app):
        """Test search history string representation."""
        with app.app_context():
            search = SearchHistory(
                user_id=1,
                job_title='Python Developer',
                location='Manchester',
                results_count=25
            )
            assert repr(search) == '<SearchHistory Python Developer in Manchester>'
    
    def test_default_results_count(self, app):
        """Test default results count."""
        with app.app_context():
            search = SearchHistory(
                user_id=1,
                job_title='Designer',
                location='Leeds'
                # results_count not specified
            )
            # Default should be None, not 0
            assert search.results_count is None
    
    def test_search_date_auto_set(self, app):
        """Test that search_date is automatically set."""
        with app.app_context():
            before_creation = datetime.utcnow()
            
            search = SearchHistory(
                user_id=1,
                job_title='Manager',
                location='Liverpool',
                results_count=5
            )
            
            db.session.add(search)
            db.session.commit()
            
            after_creation = datetime.utcnow()
            
            assert before_creation <= search.search_date <= after_creation