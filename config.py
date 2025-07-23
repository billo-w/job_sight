import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///job_sight.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Adzuna API Configuration
    ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
    ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')
    ADZUNA_BASE_URL = 'https://api.adzuna.com/v1/api/jobs'
    
    # Azure AI Configuration
    AZURE_AI_ENDPOINT = os.environ.get('AZURE_AI_ENDPOINT')
    AZURE_AI_KEY = os.environ.get('AZURE_AI_KEY')
    AZURE_AI_MODEL = 'gpt-4o'
    
    # Pagination
    JOBS_PER_PAGE = 20
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour