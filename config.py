# Import os module for operating system interface and environment variable access
import os
# Import python-dotenv for loading environment variables from .env files
# This enables local development with environment-specific configurations
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is essential for local development where environment variables
# are stored in a .env file rather than system environment
# In production, environment variables are typically set by the deployment platform
load_dotenv()

class Config:
    """
    Application configuration class implementing the configuration object pattern.
    Centralizes all application settings and follows 12-factor app methodology.
    Uses environment variables for deployment flexibility and security.
    Provides sensible defaults for development while requiring production values.
    """
    
    # Secret key for Flask session management and CSRF protection
    # Production deployments MUST set SECRET_KEY environment variable
    # No fallback default for security - application will fail if not set
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set for security")
    
    # Database URL configuration with PostgreSQL compatibility handling
    # Retrieves DATABASE_URL from environment for deployment flexibility
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Handle Heroku PostgreSQL URL format compatibility issue
    # Heroku provides postgres:// URLs but SQLAlchemy 1.4+ requires postgresql://
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        # Replace deprecated postgres:// scheme with modern postgresql:// scheme
        # This ensures compatibility with modern SQLAlchemy versions
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # SQLAlchemy database URI with fallback to local SQLite for development
    # Production should always use DATABASE_URL environment variable
    # SQLite fallback enables local development without external database setup
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///job_sight.db'
    
    # Disable SQLAlchemy event system for performance optimization
    # This feature tracks object modifications but adds overhead
    # Setting to False improves performance in production environments
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Adzuna Jobs API configuration for external job search integration
    # Application ID for Adzuna API authentication
    # Must be obtained from Adzuna developer portal and set as environment variable
    ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
    
    # Application key for Adzuna API authentication
    # Must be obtained from Adzuna developer portal and set as environment variable
    # This is a secret value and should never be hardcoded
    ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')
    
    # Base URL for Adzuna Jobs API endpoints
    # This is a public API endpoint that doesn't change frequently
    # Hardcoded as it's not sensitive and rarely changes
    ADZUNA_BASE_URL = 'https://api.adzuna.com/v1/api/jobs'
    
    # Azure AI service configuration for job market analysis
    # Azure AI endpoint URL for API requests
    # Must be obtained from Azure portal and set as environment variable
    AZURE_AI_ENDPOINT = os.environ.get('AZURE_AI_ENDPOINT')
    
    # Azure AI access key for authentication
    # Must be obtained from Azure portal and set as environment variable
    # This is a secret value and should never be hardcoded
    AZURE_AI_KEY = os.environ.get('AZURE_AI_KEY')
    
    # Azure AI model specification for consistent API behavior
    # Specifies which AI model to use for job market analysis
    # GPT-4o provides advanced language understanding for job descriptions
    AZURE_AI_MODEL = 'gpt-4o'
    
    # Pagination configuration for job search results
    # Controls how many jobs are displayed per page for performance
    # Balances user experience with API rate limits and page load times
    JOBS_PER_PAGE = 20
    
    # Session configuration for user authentication management
    # Sets session timeout in seconds (3600 = 1 hour)
    # Balances security (shorter sessions) with user experience (longer sessions)
    # After this time, users must re-authenticate for security
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour