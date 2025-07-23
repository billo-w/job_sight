from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters.')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters.')
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class JobSearchForm(FlaskForm):
    job_title = StringField('Job Title', validators=[
        DataRequired(message='Please enter a job title to search for.')
    ], render_kw={"placeholder": "e.g. Software Engineer, Marketing Manager"})
    
    location = StringField('Location', validators=[
        DataRequired(message='Please enter a location to search in.')
    ], render_kw={"placeholder": "e.g. London, Manchester, Birmingham"})
    
    submit = SubmitField('Search Jobs')

class SaveJobForm(FlaskForm):
    job_id = StringField('Job ID', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    salary_min = StringField('Minimum Salary')
    salary_max = StringField('Maximum Salary')
    job_url = StringField('Job URL', validators=[DataRequired()])
    description = TextAreaField('Job Description')
    submit = SubmitField('Save Job')