# Import Flask-SQLAlchemy for ORM (Object-Relational Mapping) functionality
from flask_sqlalchemy import SQLAlchemy
# Import UserMixin from Flask-Login for user authentication interface
from flask_login import UserMixin
# Import Werkzeug security functions for password hashing and verification
from werkzeug.security import generate_password_hash, check_password_hash
# Import datetime for timestamp operations
from datetime import datetime

# Create SQLAlchemy instance - this is the database object that manages all ORM operations
# This instance will be initialized with the Flask app in the application factory
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model representing registered users in the system.
    Inherits from UserMixin to provide Flask-Login authentication methods.
    Implements secure password storage using Werkzeug password hashing.
    """
    # Define explicit table name for database consistency
    __tablename__ = 'users'
    
    # Primary key column - auto-incrementing integer for unique user identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Username column with unique constraint to prevent duplicate usernames
    # String(80) limits username length for database efficiency
    # nullable=False ensures username is always provided
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # Email column with unique constraint for user identification and communication
    # String(120) accommodates most email address lengths
    # nullable=False ensures email is always provided
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Password hash column - stores hashed password, never plain text
    # String(255) accommodates various hashing algorithm outputs
    # nullable=False ensures password is always set
    password_hash = db.Column(db.String(255), nullable=False)
    
    # First name column for personalization and user identification
    # String(50) provides reasonable length limit for names
    # nullable=False ensures first name is always provided
    first_name = db.Column(db.String(50), nullable=False)
    
    # Last name column for complete user identification
    # String(50) provides reasonable length limit for names
    # nullable=False ensures last name is always provided
    last_name = db.Column(db.String(50), nullable=False)
    
    # Created timestamp - automatically set when user record is created
    # default=datetime.utcnow sets timestamp at record creation
    # UTC timezone ensures consistent timestamps across deployments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Updated timestamp - automatically updated when user record is modified
    # default=datetime.utcnow sets initial timestamp
    # onupdate=datetime.utcnow updates timestamp on any record modification
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define one-to-many relationship with SavedJob model
    # backref='user' creates reverse relationship on SavedJob model
    # lazy=True means related objects are loaded on-demand for performance
    # cascade='all, delete-orphan' ensures saved jobs are deleted when user is deleted
    saved_jobs = db.relationship('SavedJob', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Define one-to-many relationship with SearchHistory model
    # backref='user' creates reverse relationship on SearchHistory model
    # lazy=True means related objects are loaded on-demand for performance
    # cascade='all, delete-orphan' ensures search history is deleted when user is deleted
    search_history = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set the user's password using Werkzeug security functions.
        This method ensures passwords are never stored in plain text.
        Uses PBKDF2 hashing algorithm with salt for security.
        """
        # Generate password hash using Werkzeug's secure hashing function
        # This creates a salted hash that is computationally expensive to crack
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Check if the provided password matches the user's stored password hash.
        Uses constant-time comparison to prevent timing attacks.
        Returns True if password matches, False otherwise.
        """
        # Use Werkzeug's secure password verification function
        # This function handles the hashing and comparison securely
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """
        Return the user's full name by combining first and last names.
        Useful for display purposes in templates and user interfaces.
        """
        # Concatenate first and last name with space separator
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        """
        String representation of User object for debugging and logging.
        Returns a readable format showing the username.
        """
        # Return formatted string with username for easy identification
        return f'<User {self.username}>'

class SavedJob(db.Model):
    """
    SavedJob model representing jobs saved by users for later reference.
    Implements foreign key relationship with User model.
    Includes unique constraint to prevent duplicate saves.
    """
    # Define explicit table name for database consistency
    __tablename__ = 'saved_jobs'
    
    # Primary key column - auto-incrementing integer for unique record identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key column linking to User model
    # db.ForeignKey('users.id') creates referential integrity constraint
    # nullable=False ensures every saved job belongs to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # External job ID from Adzuna API for job identification
    # String(100) accommodates various external ID formats
    # nullable=False ensures job ID is always provided
    job_id = db.Column(db.String(100), nullable=False)
    
    # Job title for display and search purposes
    # String(255) accommodates most job title lengths
    # nullable=False ensures job title is always provided
    job_title = db.Column(db.String(255), nullable=False)
    
    # Company name for job identification and filtering
    # String(255) accommodates most company name lengths
    # nullable=False ensures company is always provided
    company = db.Column(db.String(255), nullable=False)
    
    # Job location for geographical filtering and display
    # String(255) accommodates detailed location descriptions
    # nullable=False ensures location is always provided
    location = db.Column(db.String(255), nullable=False)
    
    # Minimum salary value using Numeric type for precise decimal handling
    # Numeric(10, 2) allows up to 8 digits before decimal and 2 after
    # nullable=True because salary information may not always be available
    salary_min = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Maximum salary value using Numeric type for precise decimal handling
    # Numeric(10, 2) allows up to 8 digits before decimal and 2 after
    # nullable=True because salary information may not always be available
    salary_max = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Job URL for linking back to original job posting
    # Text type accommodates long URLs without length restrictions
    # nullable=False ensures job URL is always provided for access
    job_url = db.Column(db.Text, nullable=False)
    
    # Job description for detailed job information storage
    # Text type accommodates long descriptions without length restrictions
    # nullable=True because description may not always be available
    description = db.Column(db.Text, nullable=True)
    
    # Saved timestamp - automatically set when job is saved
    # default=datetime.utcnow sets timestamp at record creation
    # UTC timezone ensures consistent timestamps across deployments
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define unique constraint to prevent users from saving the same job multiple times
    # This creates a composite unique index on user_id and job_id columns
    # name='unique_user_job' provides explicit constraint name for database management
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job'),)
    
    def get_salary_range(self):
        """
        Return formatted salary range string for display purposes.
        Handles various salary scenarios: range, minimum only, maximum only, or none.
        Returns user-friendly formatted string with currency symbol.
        """
        # Check if both minimum and maximum salary values exist
        if self.salary_min and self.salary_max:
            # Format as range with thousand separators and no decimal places
            return f"£{self.salary_min:,.0f} - £{self.salary_max:,.0f}"
        # Check if only minimum salary exists
        elif self.salary_min:
            # Format as minimum with plus sign indicating "or more"
            return f"£{self.salary_min:,.0f}+"
        # Check if only maximum salary exists
        elif self.salary_max:
            # Format as maximum with "Up to" prefix
            return f"Up to £{self.salary_max:,.0f}"
        # Return default message when no salary information is available
        return "Salary not specified"
    
    def __repr__(self):
        """
        String representation of SavedJob object for debugging and logging.
        Returns a readable format showing job title and company.
        """
        # Return formatted string with job title and company for easy identification
        return f'<SavedJob {self.job_title} at {self.company}>'

class SearchHistory(db.Model):
    """
    SearchHistory model representing user's job search history.
    Tracks search patterns for analytics and user experience improvement.
    Implements foreign key relationship with User model.
    """
    # Define explicit table name for database consistency
    __tablename__ = 'search_history'
    
    # Primary key column - auto-incrementing integer for unique record identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key column linking to User model
    # db.ForeignKey('users.id') creates referential integrity constraint
    # nullable=False ensures every search belongs to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Job title searched by user for tracking search patterns
    # String(255) accommodates most job title search terms
    # nullable=False ensures job title is always recorded
    job_title = db.Column(db.String(255), nullable=False)
    
    # Location searched by user for geographical search analysis
    # String(255) accommodates detailed location search terms
    # nullable=False ensures location is always recorded
    location = db.Column(db.String(255), nullable=False)
    
    # Search timestamp - automatically set when search is performed
    # default=datetime.utcnow sets timestamp at record creation
    # UTC timezone ensures consistent timestamps across deployments
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Number of results returned by the search for analytics
    # Integer type for counting search result quantities
    # nullable=False with default=0 ensures count is always recorded
    # default=0 handles cases where search returns no results
    results_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        """
        String representation of SearchHistory object for debugging and logging.
        Returns a readable format showing job title and location searched.
        """
        # Return formatted string with search terms for easy identification
        return f'<SearchHistory {self.job_title} in {self.location}>'