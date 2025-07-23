import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AdzunaAPI:
    """Service class for interacting with the Adzuna Jobs API."""
    
    def __init__(self):
        self.app_id = current_app.config.get('ADZUNA_APP_ID')
        self.app_key = current_app.config.get('ADZUNA_APP_KEY')
        self.base_url = current_app.config.get('ADZUNA_BASE_URL')
        
        if not all([self.app_id, self.app_key]):
            logger.warning("Adzuna API credentials not configured")
    
    def search_jobs(self, job_title, location, page=1, results_per_page=20):
        """
        Search for jobs using the Adzuna API.
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in
            page (int): Page number for pagination (default: 1)
            results_per_page (int): Number of results per page (default: 20)
        
        Returns:
            dict: API response containing job listings and metadata
        """
        if not all([self.app_id, self.app_key]):
            return {
                'error': 'Adzuna API credentials not configured',
                'results': [],
                'count': 0
            }
        
        try:
            # Construct the API endpoint URL
            country = 'gb'  # UK jobs
            url = f"{self.base_url}/{country}/search/{page}"
            
            # Prepare query parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': job_title,
                'where': location,
                'results_per_page': results_per_page,
                'sort_by': 'relevance'
            }
            
            # Make the API request
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Check if response content type is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"Adzuna API returned non-JSON response. Content-Type: {content_type}")
                return {
                    'error': 'API returned invalid response format',
                    'results': [],
                    'count': 0
                }
            
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response from Adzuna API: {str(e)}")
                return {
                    'error': 'Failed to parse API response',
                    'results': [],
                    'count': 0
                }
            
            # Ensure data is a dictionary
            if not isinstance(data, dict):
                logger.error(f"Adzuna API returned unexpected data type: {type(data)}")
                return {
                    'error': 'API returned unexpected data format',
                    'results': [],
                    'count': 0
                }
            
            # Process and format the job results
            formatted_jobs = []
            for job in data.get('results', []):
                formatted_job = self._format_job(job)
                formatted_jobs.append(formatted_job)
            
            # Safely extract location suggestions
            location_suggestions = location  # Default to the input location
            class_data = data.get('__CLASS__', {})
            if isinstance(class_data, dict):
                location_data = class_data.get('location', {})
                if isinstance(location_data, dict):
                    location_suggestions = location_data.get('display_name', location)
            
            return {
                'results': formatted_jobs,
                'count': data.get('count', 0),
                'page': page,
                'total_pages': (data.get('count', 0) + results_per_page - 1) // results_per_page,
                'location_suggestions': location_suggestions
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request failed: {str(e)}")
            return {
                'error': f'Failed to fetch jobs: {str(e)}',
                'results': [],
                'count': 0
            }
        except Exception as e:
            logger.error(f"Unexpected error in Adzuna API: {str(e)}")
            return {
                'error': 'An unexpected error occurred while searching for jobs',
                'results': [],
                'count': 0
            }
    
    def _format_job(self, job_data):
        """
        Format a single job result from the Adzuna API.
        
        Args:
            job_data (dict): Raw job data from the API
        
        Returns:
            dict: Formatted job data
        """
        # Ensure job_data is a dictionary
        if not isinstance(job_data, dict):
            logger.warning(f"Expected dict for job_data, got {type(job_data)}: {job_data}")
            return {
                'id': '',
                'title': 'Invalid job data',
                'company': 'Unknown',
                'location': 'Unknown',
                'description': 'Job data format error',
                'salary_min': None,
                'salary_max': None,
                'salary_is_predicted': False,
                'contract_type': 'Not specified',
                'contract_time': 'Not specified',
                'created': '',
                'redirect_url': '',
                'category': 'Other',
                'adref': ''
            }
        
        # Safely extract company information
        company_data = job_data.get('company', {})
        company_name = 'Company not specified'
        if isinstance(company_data, dict):
            company_name = company_data.get('display_name', 'Company not specified')
        elif isinstance(company_data, str):
            company_name = company_data
        
        # Safely extract location information
        location_data = job_data.get('location', {})
        location_name = 'Location not specified'
        if isinstance(location_data, dict):
            location_name = location_data.get('display_name', 'Location not specified')
        elif isinstance(location_data, str):
            location_name = location_data
        
        # Safely extract category information
        category_data = job_data.get('category', {})
        category_name = 'Other'
        if isinstance(category_data, dict):
            category_name = category_data.get('label', 'Other')
        elif isinstance(category_data, str):
            category_name = category_data
        
        return {
            'id': job_data.get('id', ''),
            'title': job_data.get('title', 'No title available'),
            'company': company_name,
            'location': location_name,
            'description': job_data.get('description', 'No description available'),
            'salary_min': job_data.get('salary_min'),
            'salary_max': job_data.get('salary_max'),
            'salary_is_predicted': job_data.get('salary_is_predicted', False),
            'contract_type': job_data.get('contract_type', 'Not specified'),
            'contract_time': job_data.get('contract_time', 'Not specified'),
            'created': job_data.get('created', ''),
            'redirect_url': job_data.get('redirect_url', ''),
            'category': category_name,
            'adref': job_data.get('adref', '')
        }
    
    def get_job_categories(self):
        """
        Get available job categories from Adzuna API.
        
        Returns:
            list: List of job categories
        """
        if not all([self.app_id, self.app_key]):
            return []
        
        try:
            country = 'gb'
            url = f"{self.base_url}/{country}/categories"
            
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Check if response content type is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"Adzuna categories API returned non-JSON response. Content-Type: {content_type}")
                return []
            
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response from Adzuna categories API: {str(e)}")
                return []
            
            # Ensure data is a dictionary
            if not isinstance(data, dict):
                logger.error(f"Adzuna categories API returned unexpected data type: {type(data)}")
                return []
            
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch job categories: {str(e)}")
            return []
    
    def format_salary(self, salary_min, salary_max, is_predicted=False):
        """
        Format salary information for display.
        
        Args:
            salary_min (float): Minimum salary
            salary_max (float): Maximum salary
            is_predicted (bool): Whether the salary is predicted
        
        Returns:
            str: Formatted salary string
        """
        if not salary_min and not salary_max:
            return "Salary not specified"
        
        predicted_text = " (estimated)" if is_predicted else ""
        
        if salary_min and salary_max:
            return f"£{salary_min:,.0f} - £{salary_max:,.0f}{predicted_text}"
        elif salary_min:
            return f"£{salary_min:,.0f}+{predicted_text}"
        elif salary_max:
            return f"Up to £{salary_max:,.0f}{predicted_text}"
        
        return "Salary not specified"