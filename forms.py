# Import Flask-WTF for form handling with CSRF protection
from flask_wtf import FlaskForm
# Import WTForms field types for different input types
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
# Import WTForms validators for input validation and security
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
# Import User model for custom validation checks
from models import User

class RegistrationForm(FlaskForm):
    """
    User registration form with comprehensive validation.
    Inherits from FlaskForm which provides CSRF protection automatically.
    Implements custom validators to ensure unique usernames and emails.
    """
    
    # First name field with length validation for data integrity
    first_name = StringField('First Name', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # Length validator ensures name is within reasonable bounds
        # min=2 prevents single character names, max=50 prevents database overflow
        Length(min=2, max=50, message='First name must be between 2 and 50 characters.')
    ])
    
    # Last name field with identical validation to first name
    last_name = StringField('Last Name', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # Length validator ensures name is within reasonable bounds
        # min=2 prevents single character names, max=50 prevents database overflow
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters.')
    ])
    
    # Username field with length validation for security and usability
    username = StringField('Username', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # Length validator ensures username is within reasonable bounds
        # min=4 prevents very short usernames, max=20 ensures database compatibility
        Length(min=4, max=20, message='Username must be between 4 and 20 characters.')
    ])
    
    # Email field with email format validation
    email = StringField('Email', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # Email() validator checks for valid email format using regex
        # Prevents invalid email addresses from being submitted
        Email(message='Please enter a valid email address.')
    ])
    
    # Password field with minimum length requirement for security
    password = PasswordField('Password', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # Length validator enforces minimum password length for security
        # min=8 follows modern password security recommendations
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    
    # Password confirmation field to prevent typos in password entry
    password2 = PasswordField('Confirm Password', validators=[
        # DataRequired() ensures field is not empty or whitespace-only
        DataRequired(),
        # EqualTo validator ensures both password fields match exactly
        # Prevents user registration with mistyped passwords
        EqualTo('password', message='Passwords must match.')
    ])
    
    # Submit button for form submission
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Custom validator method for username uniqueness.
        WTForms automatically calls methods named validate_<fieldname>.
        Queries database to ensure username is not already taken.
        Raises ValidationError if username exists.
        """
        # Query database for existing user with this username
        user = User.query.filter_by(username=username.data).first()
        # If user exists, raise validation error to prevent duplicate usernames
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validator method for email uniqueness.
        WTForms automatically calls methods named validate_<fieldname>.
        Queries database to ensure email is not already registered.
        Raises ValidationError if email exists.
        """
        # Query database for existing user with this email address
        user = User.query.filter_by(email=email.data).first()
        # If user exists, raise validation error to prevent duplicate emails
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    """
    User login form with basic validation.
    Inherits from FlaskForm which provides CSRF protection automatically.
    Simple form with minimal validation for user authentication.
    """
    
    # Username field for user identification
    # DataRequired() ensures field is not empty for authentication
    username = StringField('Username', validators=[DataRequired()])
    
    # Password field for user authentication
    # DataRequired() ensures field is not empty for authentication
    password = PasswordField('Password', validators=[DataRequired()])
    
    # Submit button for form submission
    submit = SubmitField('Sign In')

class JobSearchForm(FlaskForm):
    """
    Job search form for querying external job APIs.
    Inherits from FlaskForm which provides CSRF protection automatically.
    Includes placeholder text for better user experience.
    """
    
    # Job title field with validation and user guidance
    job_title = StringField('Job Title', validators=[
        # DataRequired() with custom message for better user feedback
        DataRequired(message='Please enter a job title to search for.')
    ], render_kw={"placeholder": "e.g. Software Engineer, Marketing Manager"})
    # render_kw adds HTML attributes to the field for better UX
    
    # Location field with validation and user guidance
    location = StringField('Location', validators=[
        # DataRequired() with custom message for better user feedback
        DataRequired(message='Please enter a location to search in.')
    ], render_kw={"placeholder": "e.g. London, Manchester, Birmingham"})
    # render_kw adds HTML attributes to the field for better UX
    
    # Submit button for form submission
    submit = SubmitField('Search Jobs')

class SaveJobForm(FlaskForm):
    """
    Form for saving job details to user's saved jobs list.
    Inherits from FlaskForm which provides CSRF protection automatically.
    Used for AJAX requests to save job information securely.
    """
    
    # External job ID from API for unique identification
    # DataRequired() ensures job ID is always provided
    job_id = StringField('Job ID', validators=[DataRequired()])
    
    # Job title for display and search purposes
    # DataRequired() ensures job title is always provided
    job_title = StringField('Job Title', validators=[DataRequired()])
    
    # Company name for job identification
    # DataRequired() ensures company name is always provided
    company = StringField('Company', validators=[DataRequired()])
    
    # Job location for geographical reference
    # DataRequired() ensures location is always provided
    location = StringField('Location', validators=[DataRequired()])
    
    # Minimum salary - optional field as salary may not be specified
    # No validators as this field is optional
    salary_min = StringField('Minimum Salary')
    
    # Maximum salary - optional field as salary may not be specified
    # No validators as this field is optional
    salary_max = StringField('Maximum Salary')
    
    # Job URL for linking back to original posting
    # DataRequired() ensures URL is always provided for job access
    job_url = StringField('Job URL', validators=[DataRequired()])
    
    # Job description - optional field for detailed job information
    # TextAreaField allows for longer text input
    # No validators as this field is optional
    description = TextAreaField('Job Description')
    
    # Submit button for form submission
    submit = SubmitField('Save Job')