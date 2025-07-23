from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_jobs = db.relationship('SavedJob', backref='user', lazy=True, cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    salary_min = db.Column(db.Numeric(10, 2), nullable=True)
    salary_max = db.Column(db.Numeric(10, 2), nullable=True)
    job_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate saves
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job'),)
    
    def get_salary_range(self):
        """Return formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"£{self.salary_min:,.0f} - £{self.salary_max:,.0f}"
        elif self.salary_min:
            return f"£{self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to £{self.salary_max:,.0f}"
        return "Salary not specified"
    
    def __repr__(self):
        return f'<SavedJob {self.job_title} at {self.company}>'

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    results_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<SearchHistory {self.job_title} in {self.location}>'