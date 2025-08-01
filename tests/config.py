import os
import tempfile

class TestConfig:
    """Test configuration that completely overrides production settings."""
    
    def __init__(self):
        # Create a temporary file for the test database
        self.db_fd, self.db_path = tempfile.mkstemp()
    
    SECRET_KEY = 'test-secret-key'
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Force SQLite for testing
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'sqlite:///{self.db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Test API configurations
    ADZUNA_APP_ID = 'test-app-id'
    ADZUNA_APP_KEY = 'test-app-key'
    AZURE_AI_ENDPOINT = 'https://test.openai.azure.com/'
    AZURE_AI_KEY = 'test-azure-key'
    JOBS_PER_PAGE = 20
    
    def cleanup(self):
        """Clean up temporary database file."""
        try:
            os.close(self.db_fd)
            os.unlink(self.db_path)
        except:
            pass