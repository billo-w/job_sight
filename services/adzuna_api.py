# Import the requests library for making HTTP API calls to external services
# This is the standard Python library for HTTP client operations
import requests
# Import Flask's current_app to access application configuration in a thread-safe manner
# current_app provides access to the Flask application context and configuration
from flask import current_app
# Import logging module for structured application logging and monitoring
# Essential for DevOps observability and debugging in production environments
import logging

# Create a logger instance specific to this module for traceability and debugging
# Using __name__ ensures log messages are properly namespaced for this service
# This enables granular log filtering and monitoring in production systems
logger = logging.getLogger(__name__)

class AdzunaAPI:
    """
    Service class for interacting with the Adzuna Jobs API.
    
    This class implements the Service Layer pattern, providing a clean abstraction
    over external API interactions. It demonstrates DevOps best practices including:
    - Configuration management through Flask config (12-factor app principle)
    - Comprehensive error handling and resilience patterns
    - Structured logging for monitoring and debugging
    - Data validation and transformation
    - Timeout handling for external service calls
    - Circuit breaker pattern for graceful degradation
    """
    
    def __init__(self):
        """
        Initialize the Adzuna API service with configuration from Flask app context.
        
        DevOps Pattern: Configuration Injection
        - Credentials are injected from environment-specific configuration
        - No hardcoded values, supporting different environments (dev/staging/prod)
        - Fail-fast pattern: warns if credentials are missing but doesn't crash
        - Follows 12-factor app methodology for configuration management
        """
        # Retrieve Adzuna API application ID from Flask configuration
        # This supports environment-specific configuration management
        # Configuration should be set via environment variables in production
        self.app_id = current_app.config.get('ADZUNA_APP_ID')
        
        # Retrieve Adzuna API key from Flask configuration
        # Sensitive credentials are managed through configuration, not hardcoded
        # In production, this should come from secure secret management systems
        self.app_key = current_app.config.get('ADZUNA_APP_KEY')
        
        # Retrieve base URL for Adzuna API endpoints
        # Allows for different API environments (sandbox vs production)
        # Enables easy switching between API versions or endpoints
        self.base_url = current_app.config.get('ADZUNA_BASE_URL')
        
        # Validate that required credentials are present at initialization
        # Defensive programming: check dependencies early to fail fast
        # This prevents runtime errors and enables proactive monitoring
        if not all([self.app_id, self.app_key]):
            # Log warning for monitoring systems to detect configuration issues
            # This enables proactive alerting on missing credentials
            # Warning level allows service to continue but alerts operations team
            logger.warning("Adzuna API credentials not configured")
    
    def search_jobs(self, job_title, location, page=1, results_per_page=20):
        """
        Search for jobs using the Adzuna API with comprehensive error handling.
        
        This method demonstrates several DevOps patterns:
        - Circuit breaker pattern (early return on missing credentials)
        - Timeout handling for external service resilience
        - Comprehensive error handling with different error types
        - Data validation and sanitization
        - Structured response format for consistent API contracts
        - Retry-friendly design (stateless operations)
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in
            page (int): Page number for pagination (default: 1)
            results_per_page (int): Number of results per page (default: 20)
        
        Returns:
            dict: API response containing job listings and metadata
        """
        # Circuit breaker pattern: fail fast if credentials are not configured
        # Prevents unnecessary API calls and provides clear error messaging
        # This pattern improves system resilience and reduces external API load
        if not all([self.app_id, self.app_key]):
            # Return standardized error response structure
            # Consistent error format enables better error handling in calling code
            # This supports automated error detection and monitoring
            return {
                'error': 'Adzuna API credentials not configured',
                'results': [],
                'count': 0
            }
        
        # Comprehensive try-catch block for robust error handling
        # Different exception types are handled appropriately for better debugging
        # This enables proper error categorization for monitoring and alerting
        try:
            # Construct the API endpoint URL using string formatting
            # Hardcoded to 'gb' for UK jobs - could be parameterized for internationalization
            # This demonstrates RESTful API endpoint construction patterns
            country = 'gb'  # UK jobs
            # Build RESTful API endpoint following Adzuna's URL structure
            # f-string formatting provides readable and maintainable URL construction
            url = f"{self.base_url}/{country}/search/{page}"
            
            # Prepare query parameters dictionary for the HTTP request
            # Separating parameters improves readability and maintainability
            # This pattern makes it easy to add/remove parameters and supports testing
            params = {
                'app_id': self.app_id,           # API authentication identifier
                'app_key': self.app_key,         # API authentication key
                'what': job_title,               # Job title search parameter
                'where': location,               # Location search parameter
                'results_per_page': results_per_page,  # Pagination control
                'sort_by': 'relevance'          # Sort results by relevance for better UX
            }
            
            # Make HTTP GET request to external API with timeout for resilience
            # Timeout prevents hanging requests that could impact application performance
            # 10-second timeout balances responsiveness with API reliability
            response = requests.get(url, params=params, timeout=10)
            
            # Raise exception for HTTP error status codes (4xx, 5xx)
            # This converts HTTP errors into Python exceptions for consistent error handling
            # Enables proper error propagation and logging for monitoring systems
            response.raise_for_status()
            
            # Validate response content type to ensure we received JSON
            # Content-Type validation prevents parsing errors from unexpected response formats
            # This defensive programming pattern improves system reliability
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                # Log error with specific details for debugging and monitoring
                # Include content-type for troubleshooting API changes or issues
                logger.error(f"Adzuna API returned non-JSON response. Content-Type: {content_type}")
                # Return standardized error response for consistent error handling
                return {
                    'error': 'API returned invalid response format',
                    'results': [],
                    'count': 0
                }
            
            # Parse JSON response with error handling for malformed JSON
            # Separate try-catch for JSON parsing provides specific error handling
            # This enables differentiation between network and parsing errors
            try:
                # Attempt to parse the response body as JSON
                # This may fail if the API returns malformed JSON
                data = response.json()
            except ValueError as e:
                # Log JSON parsing errors with exception details for debugging
                # Include the actual error message for troubleshooting
                logger.error(f"Failed to parse JSON response from Adzuna API: {str(e)}")
                # Return user-friendly error message while logging technical details
                return {
                    'error': 'Failed to parse API response',
                    'results': [],
                    'count': 0
                }
            
            # Validate that parsed data is a dictionary as expected
            # Type validation prevents runtime errors from unexpected data structures
            # This defensive programming pattern improves system stability
            if not isinstance(data, dict):
                # Log unexpected data type for monitoring and debugging
                # Include actual type information for troubleshooting
                logger.error(f"Adzuna API returned unexpected data type: {type(data)}")
                # Return standardized error response
                return {
                    'error': 'API returned unexpected data format',
                    'results': [],
                    'count': 0
                }
            
            # Process and format the job results using helper method
            # Separation of concerns: data transformation is handled separately
            # This modular approach improves testability and maintainability
            formatted_jobs = []
            # Iterate through job results with safe dictionary access
            # .get() method provides default empty list if 'results' key is missing
            for job in data.get('results', []):
                # Transform each job using dedicated formatting method
                # This ensures consistent data structure across the application
                formatted_job = self._format_job(job)
                # Add formatted job to results list
                formatted_jobs.append(formatted_job)
            
            # Safely extract location suggestions from nested API response structure
            # Default to input location if API doesn't provide suggestions
            # This provides fallback behavior for better user experience
            location_suggestions = location  # Default to the input location
            
            # Navigate nested dictionary structure safely to extract location data
            # Safe navigation prevents KeyError exceptions from missing data
            # This defensive programming pattern handles API response variations
            class_data = data.get('__CLASS__', {})
            # Check if class_data is actually a dictionary before accessing nested keys
            if isinstance(class_data, dict):
                # Extract location data from nested structure
                location_data = class_data.get('location', {})
                # Verify location_data is a dictionary before accessing display_name
                if isinstance(location_data, dict):
                    # Use API-provided location display name if available
                    # Fall back to original location if display_name is not present
                    location_suggestions = location_data.get('display_name', location)
            
            # Return standardized response structure with all required fields
            # Consistent response format enables reliable client-side processing
            # This contract-based approach supports API versioning and evolution
            return {
                'results': formatted_jobs,                    # List of formatted job objects
                'count': data.get('count', 0),               # Total number of jobs found
                'page': page,                                 # Current page number
                # Calculate total pages using ceiling division for pagination
                # This mathematical approach ensures correct page count calculation
                'total_pages': (data.get('count', 0) + results_per_page - 1) // results_per_page,
                'location_suggestions': location_suggestions  # Location suggestions for UX
            }
            
        # Handle HTTP-related exceptions (network errors, timeouts, HTTP errors)
        # RequestException is the base class for all requests-related exceptions
        except requests.exceptions.RequestException as e:
            # Log specific request exception details for debugging and monitoring
            # Include the actual error message for troubleshooting network issues
            logger.error(f"Adzuna API request failed: {str(e)}")
            # Return user-friendly error message with technical details for debugging
            # This balances user experience with operational visibility
            return {
                'error': f'Failed to fetch jobs: {str(e)}',
                'results': [],
                'count': 0
            }
        # Catch-all exception handler for unexpected errors
        # This ensures the method never raises unhandled exceptions
        except Exception as e:
            # Log unexpected exceptions for debugging and monitoring
            # This helps identify new error conditions that need specific handling
            logger.error(f"Unexpected error in Adzuna API: {str(e)}")
            # Return generic error message to avoid exposing internal details
            # This security practice prevents information leakage
            return {
                'error': 'An unexpected error occurred while searching for jobs',
                'results': [],
                'count': 0
            }
    
    def _format_job(self, job_data):
        """
        Format a single job result from the Adzuna API into standardized structure.
        
        This private method demonstrates:
        - Data transformation and normalization patterns
        - Defensive programming with type checking
        - Safe navigation of nested data structures
        - Default value handling for missing data
        - Consistent output format for API contracts
        - Error recovery and graceful degradation
        
        Args:
            job_data (dict): Raw job data from the API
        
        Returns:
            dict: Formatted job data with standardized fields
        """
        # Validate input data type to prevent runtime errors
        # Type checking is essential for robust data processing
        # This defensive programming pattern prevents downstream errors
        if not isinstance(job_data, dict):
            # Log warning about invalid data for monitoring and debugging
            # Include actual data type and value for troubleshooting
            logger.warning(f"Expected dict for job_data, got {type(job_data)}: {job_data}")
            # Return default job structure with error indicators
            # Graceful degradation: return valid structure even with bad input
            # This prevents application crashes and maintains service availability
            return {
                'id': '',                           # Empty ID for invalid data
                'title': 'Invalid job data',        # Error indicator in title
                'company': 'Unknown',               # Default company name
                'location': 'Unknown',              # Default location
                'description': 'Job data format error',  # Error description
                'salary_min': None,                 # No salary data available
                'salary_max': None,                 # No salary data available
                'salary_is_predicted': False,       # Not predicted salary
                'contract_type': 'Not specified',   # Default contract type
                'contract_time': 'Not specified',   # Default contract time
                'created': '',                      # Empty creation date
                'redirect_url': '',                 # Empty redirect URL
                'category': 'Other',                # Default category
                'adref': ''                         # Empty ad reference
            }
        
        # Safely extract company information with type checking
        # Handle both dictionary and string formats for company data
        # This flexibility accommodates API response variations
        company_data = job_data.get('company', {})
        company_name = 'Company not specified'  # Default value for missing data
        # Check if company data is provided as a dictionary (most common format)
        if isinstance(company_data, dict):
            # Extract display name from company dictionary with fallback
            # .get() method provides safe access with default value
            company_name = company_data.get('display_name', 'Company not specified')
        # Handle case where company data is provided as a simple string
        elif isinstance(company_data, str):
            # Use the string directly as company name
            company_name = company_data
        
        # Safely extract location information with type checking
        # Similar pattern to company extraction for consistency
        # This handles API response format variations gracefully
        location_data = job_data.get('location', {})
        location_name = 'Location not specified'  # Default value for missing data
        # Check if location data is provided as a dictionary (most common format)
        if isinstance(location_data, dict):
            # Extract display name from location dictionary with fallback
            location_name = location_data.get('display_name', 'Location not specified')
        # Handle case where location data is provided as a simple string
        elif isinstance(location_data, str):
            # Use the string directly as location name
            location_name = location_data
        
        # Safely extract category information with type checking
        # Categories help with job classification and filtering
        # This pattern ensures consistent category handling
        category_data = job_data.get('category', {})
        category_name = 'Other'  # Default category for unclassified jobs
        # Check if category data is provided as a dictionary (most common format)
        if isinstance(category_data, dict):
            # Extract label from category dictionary with fallback
            # 'label' is the standard field name for category display text
            category_name = category_data.get('label', 'Other')
        # Handle case where category data is provided as a simple string
        elif isinstance(category_data, str):
            # Use the string directly as category name
            category_name = category_data
        
        # Return standardized job data structure
        # This consistent format enables reliable processing throughout the application
        # All fields have appropriate defaults to prevent None/null errors
        return {
            # Job identifier - empty string if not provided (safer than None)
            'id': job_data.get('id', ''),
            # Job title with user-friendly default for missing titles
            'title': job_data.get('title', 'No title available'),
            # Company name extracted and formatted above
            'company': company_name,
            # Location name extracted and formatted above
            'location': location_name,
            # Job description with user-friendly default for missing descriptions
            'description': job_data.get('description', 'No description available'),
            # Minimum salary - None is appropriate for numeric fields when not available
            'salary_min': job_data.get('salary_min'),
            # Maximum salary - None is appropriate for numeric fields when not available
            'salary_max': job_data.get('salary_max'),
            # Boolean flag indicating if salary is predicted/estimated
            'salary_is_predicted': job_data.get('salary_is_predicted', False),
            # Contract type (permanent, contract, etc.) with default
            'contract_type': job_data.get('contract_type', 'Not specified'),
            # Contract time (full-time, part-time, etc.) with default
            'contract_time': job_data.get('contract_time', 'Not specified'),
            # Job creation date - empty string if not provided
            'created': job_data.get('created', ''),
            # URL to redirect to job posting - empty string if not provided
            'redirect_url': job_data.get('redirect_url', ''),
            # Job category extracted and formatted above
            'category': category_name,
            # Ad reference identifier - empty string if not provided
            'adref': job_data.get('adref', '')
        }
    
    def get_job_categories(self):
        """
        Get available job categories from Adzuna API.
        
        This method demonstrates:
        - Simple API endpoint consumption
        - Consistent error handling patterns
        - Configuration validation
        - Safe data extraction
        - Graceful failure with empty results
        
        Returns:
            list: List of job categories or empty list on failure
        """
        # Circuit breaker pattern: fail fast if credentials are not configured
        # Prevents unnecessary API calls when service is not properly configured
        # This pattern improves system resilience and reduces external API load
        if not all([self.app_id, self.app_key]):
            # Return empty list instead of raising exception
            # This graceful failure pattern prevents application crashes
            return []
        
        # Comprehensive error handling for external API calls
        # This pattern ensures the method never raises unhandled exceptions
        try:
            # Set country for API endpoint (hardcoded to UK for this implementation)
            # This could be parameterized for international support
            country = 'gb'
            # Construct categories endpoint URL following Adzuna's API structure
            # RESTful endpoint design for retrieving category metadata
            url = f"{self.base_url}/{country}/categories"
            
            # Prepare authentication parameters for the API request
            # Minimal parameter set required for categories endpoint
            params = {
                'app_id': self.app_id,    # API authentication identifier
                'app_key': self.app_key   # API authentication key
            }
            
            # Make HTTP GET request with timeout for resilience
            # Same timeout pattern as search_jobs for consistency
            # Timeout prevents hanging requests in production environments
            response = requests.get(url, params=params, timeout=10)
            # Raise exception for HTTP error status codes (4xx, 5xx)
            # Consistent error handling pattern across all API methods
            response.raise_for_status()
            
            # Validate response content type to ensure we received JSON
            # Same validation pattern as search_jobs for consistency
            # This defensive programming prevents parsing errors
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                # Log error with specific details for debugging and monitoring
                # Include endpoint information for troubleshooting
                logger.error(f"Adzuna categories API returned non-JSON response. Content-Type: {content_type}")
                # Return empty list for graceful failure
                return []
            
            # Parse JSON response with error handling
            # Separate try-catch for JSON parsing provides specific error handling
            try:
                # Attempt to parse the response body as JSON
                data = response.json()
            except ValueError as e:
                # Log JSON parsing errors with exception details
                # Include endpoint context for debugging
                logger.error(f"Failed to parse JSON response from Adzuna categories API: {str(e)}")
                # Return empty list for graceful failure
                return []
            
            # Validate that parsed data is a dictionary as expected
            # Type validation prevents runtime errors from unexpected data structures
            if not isinstance(data, dict):
                # Log unexpected data type for monitoring and debugging
                logger.error(f"Adzuna categories API returned unexpected data type: {type(data)}")
                # Return empty list for graceful failure
                return []
            
            # Extract results from API response with safe dictionary access
            # .get() method provides default empty list if 'results' key is missing
            # This pattern handles API response variations gracefully
            return data.get('results', [])
            
        # Catch-all exception handler for any errors during category fetching
        # This ensures the method never raises unhandled exceptions
        except Exception as e:
            # Log all errors for debugging and monitoring
            # Include method context for troubleshooting
            logger.error(f"Failed to fetch job categories: {str(e)}")
            # Return empty list for graceful failure
            # This allows the application to continue functioning without categories
            return []
    
    def format_salary(self, salary_min, salary_max, is_predicted=False):
        """
        Format salary information for display purposes.
        
        This utility method demonstrates:
        - Data formatting and presentation logic
        - Conditional logic for different salary scenarios
        - User-friendly text generation
        - Handling of optional/missing data
        - Internationalization considerations (£ symbol)
        
        Args:
            salary_min (float): Minimum salary value
            salary_max (float): Maximum salary value
            is_predicted (bool): Whether the salary is predicted/estimated
        
        Returns:
            str: Formatted salary string for display
        """
        # Check if both salary values are missing or falsy
        # This handles None, 0, and empty values consistently
        # Early return pattern for the most common case
        if not salary_min and not salary_max:
            # Return user-friendly message for missing salary information
            return "Salary not specified"
        
        # Prepare suffix text for predicted/estimated salaries
        # This provides transparency about salary data quality
        # Conditional expression provides clean, readable code
        predicted_text = " (estimated)" if is_predicted else ""
        
        # Handle case where both minimum and maximum salaries are provided
        # This is the most informative salary format for users
        if salary_min and salary_max:
            # Format as salary range with thousands separators
            # :,.0f format provides comma-separated integers (e.g., 50,000)
            # £ symbol indicates UK currency (could be parameterized for internationalization)
            return f"£{salary_min:,.0f} - £{salary_max:,.0f}{predicted_text}"
        # Handle case where only minimum salary is provided
        elif salary_min:
            # Format as "minimum+" to indicate open-ended range
            # + symbol suggests salary could be higher based on experience
            return f"£{salary_min:,.0f}+{predicted_text}"
        # Handle case where only maximum salary is provided
        elif salary_max:
            # Format as "up to maximum" to indicate salary ceiling
            # This format is common for entry-level or capped positions
            return f"Up to £{salary_max:,.0f}{predicted_text}"
        
        # Fallback case (should not be reached due to initial check)
        # Defensive programming: provide safe default even if logic changes
        return "Salary not specified"