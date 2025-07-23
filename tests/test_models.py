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
    
    def test_get_full_name(self, test_user):
        """Test getting user's full name."""
        assert test_user.get_full_name() == 'Test User'
    
    def test_user_repr(self, test_user):
        """Test user string representation."""
        assert repr(test_user) == '<User testuser>'
    
    def test_user_relationships(self, app, test_user):
        """Test user relationships with saved jobs and search history."""
        with app.app_context():
            # Create a saved job
            saved_job = SavedJob(
                user_id=test_user.id,
                job_id='job123',
                job_title='Developer',
                company='Tech Corp',
                location='London',
                job_url='https://example.com/job'
            )
            db.session.add(saved_job)
            
            # Create search history
            search = SearchHistory(
                user_id=test_user.id,
                job_title='Python Developer',
                location='London',
                results_count=10
            )
            db.session.add(search)
            db.session.commit()
            
            # Test relationships
            assert len(test_user.saved_jobs) == 1
            assert len(test_user.search_history) == 1
            assert test_user.saved_jobs[0].job_title == 'Developer'
            assert test_user.search_history[0].job_title == 'Python Developer'


class TestSavedJob:
    """Test cases for the SavedJob model."""
    
    def test_saved_job_creation(self, app, test_user):
        """Test creating a saved job."""
        with app.app_context():
            saved_job = SavedJob(
                user_id=test_user.id,
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
            assert saved_job.user_id == test_user.id
            assert saved_job.job_id == 'unique-job-123'
            assert saved_job.job_title == 'Senior Developer'
            assert saved_job.company == 'Amazing Company'
            assert saved_job.location == 'Manchester'
            assert saved_job.salary_min == 60000
            assert saved_job.salary_max == 80000
            assert saved_job.job_url == 'https://example.com/job/123'
            assert saved_job.description == 'Great job opportunity'
            assert saved_job.saved_at is not None
    
    def test_get_salary_range(self, app, test_user):
        """Test salary range formatting."""
        with app.app_context():
            # Test with both min and max salary
            job1 = SavedJob(
                user_id=test_user.id,
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
                user_id=test_user.id,
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
                user_id=test_user.id,
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
                user_id=test_user.id,
                job_id='job4',
                job_title='Job 4',
                company='Company',
                location='Location',
                job_url='https://example.com'
            )
            assert job4.get_salary_range() == 'Salary not specified'
    
    def test_saved_job_repr(self, test_saved_job):
        """Test saved job string representation."""
        assert repr(test_saved_job) == '<SavedJob Software Engineer at Test Company>'
    
    def test_unique_constraint(self, app, test_user):
        """Test that a user cannot save the same job twice."""
        with app.app_context():
            # Create first saved job
            job1 = SavedJob(
                user_id=test_user.id,
                job_id='duplicate-job',
                job_title='Duplicate Job',
                company='Company',
                location='Location',
                job_url='https://example.com'
            )
            db.session.add(job1)
            db.session.commit()
            
            # Try to create duplicate
            job2 = SavedJob(
                user_id=test_user.id,
                job_id='duplicate-job',  # Same job_id for same user
                job_title='Another Title',
                company='Another Company',
                location='Another Location',
                job_url='https://example.com/other'
            )
            db.session.add(job2)
            
            # Should raise an integrity error
            with pytest.raises(Exception):
                db.session.commit()


class TestSearchHistory:
    """Test cases for the SearchHistory model."""
    
    def test_search_history_creation(self, app, test_user):
        """Test creating search history."""
        with app.app_context():
            search = SearchHistory(
                user_id=test_user.id,
                job_title='Data Scientist',
                location='Birmingham',
                results_count=15
            )
            
            db.session.add(search)
            db.session.commit()
            
            assert search.id is not None
            assert search.user_id == test_user.id
            assert search.job_title == 'Data Scientist'
            assert search.location == 'Birmingham'
            assert search.results_count == 15
            assert search.search_date is not None
    
    def test_search_history_repr(self, test_search_history):
        """Test search history string representation."""
        assert repr(test_search_history) == '<SearchHistory Python Developer in Manchester>'
    
    def test_default_results_count(self, app, test_user):
        """Test default results count."""
        with app.app_context():
            search = SearchHistory(
                user_id=test_user.id,
                job_title='Designer',
                location='Leeds'
                # results_count not specified
            )
            
            db.session.add(search)
            db.session.commit()
            
            assert search.results_count == 0
    
    def test_search_date_auto_set(self, app, test_user):
        """Test that search_date is automatically set."""
        with app.app_context():
            before_creation = datetime.utcnow()
            
            search = SearchHistory(
                user_id=test_user.id,
                job_title='Manager',
                location='Liverpool',
                results_count=5
            )
            
            db.session.add(search)
            db.session.commit()
            
            after_creation = datetime.utcnow()
            
            assert before_creation <= search.search_date <= after_creation