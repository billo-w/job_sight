import requests
from flask import current_app
import logging
import json

logger = logging.getLogger(__name__)

class AzureAIService:
    """Service class for interacting with Azure AI Foundry GPT-4o model."""
    
    def __init__(self):
        self.endpoint = current_app.config.get('AZURE_AI_ENDPOINT')
        self.api_key = current_app.config.get('AZURE_AI_KEY')
        self.model = current_app.config.get('AZURE_AI_MODEL', 'gpt-4o')
        
        if not all([self.endpoint, self.api_key]):
            logger.warning("Azure AI credentials not configured")
    
    def generate_job_market_summary(self, job_title, location, job_results):
        """
        Generate an AI-powered summary of the job market for a specific role and location.
        
        Args:
            job_title (str): The job title being searched
            location (str): The location being searched
            job_results (list): List of job results from the search
        
        Returns:
            dict: Contains the summary text and metadata
        """
        if not all([self.endpoint, self.api_key]):
            return {
                'summary': 'AI summary service is not configured. Please check your Azure AI credentials.',
                'error': True
            }
        
        try:
            # Prepare job data for analysis
            job_data = self._prepare_job_data(job_results)
            
            # Create the prompt for GPT-4o
            prompt = self._create_market_analysis_prompt(job_title, location, job_data)
            
            # Prepare the request payload
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert recruitment analyst providing insights about job markets. Provide concise, actionable insights for recruiters. Format your response as plain text with clear paragraphs, not markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            # Make the API call to Azure OpenAI
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Check if response content type is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"Azure AI returned non-JSON response. Content-Type: {content_type}")
                return {
                    'summary': 'Unable to generate market summary due to API response format error.',
                    'error': True
                }
            
            try:
                result = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response from Azure AI: {str(e)}")
                return {
                    'summary': 'Unable to generate market summary due to response parsing error.',
                    'error': True
                }
            
            # Ensure result is a dictionary and has expected structure
            if not isinstance(result, dict) or 'choices' not in result:
                logger.error(f"Azure AI returned unexpected response structure: {type(result)}")
                return {
                    'summary': 'Unable to generate market summary due to unexpected response format.',
                    'error': True
                }
            
            summary = result['choices'][0]['message']['content'].strip()
            
            return {
                'summary': summary,
                'error': False,
                'job_count': len(job_results),
                'location': location,
                'job_title': job_title
            }
            
        except Exception as e:
            logger.error(f"Azure AI API request failed: {str(e)}")
            return {
                'summary': f'Unable to generate market summary at this time. Please try again later.',
                'error': True,
                'error_message': str(e)
            }
    
    def _prepare_job_data(self, job_results):
        """
        Prepare job data for AI analysis by extracting key information.
        
        Args:
            job_results (list): List of job results
        
        Returns:
            dict: Summarized job data for analysis
        """
        if not job_results:
            return {
                'total_jobs': 0,
                'companies': [],
                'salary_ranges': [],
                'contract_types': [],
                'locations': []
            }
        
        companies = []
        salary_ranges = []
        contract_types = []
        locations = []
        
        for job in job_results[:20]:  # Limit to first 20 jobs for analysis
            # Ensure job is a dictionary before calling .get()
            if not isinstance(job, dict):
                logger.warning(f"Skipping invalid job data: {type(job)} - {job}")
                continue
                
            # Extract company names
            if job.get('company'):
                companies.append(job['company'])
            
            # Extract salary information
            if job.get('salary_min') or job.get('salary_max'):
                salary_info = {
                    'min': job.get('salary_min'),
                    'max': job.get('salary_max'),
                    'is_predicted': job.get('salary_is_predicted', False)
                }
                salary_ranges.append(salary_info)
            
            # Extract contract types
            if job.get('contract_type'):
                contract_types.append(job['contract_type'])
            
            # Extract locations
            if job.get('location'):
                locations.append(job['location'])
        
        return {
            'total_jobs': len(job_results),
            'companies': list(set(companies))[:10],  # Top 10 unique companies
            'salary_ranges': salary_ranges,
            'contract_types': list(set(contract_types)),
            'locations': list(set(locations))[:5]  # Top 5 unique locations
        }
    
    def _create_market_analysis_prompt(self, job_title, location, job_data):
        """
        Create a prompt for the AI model to analyze the job market.
        
        Args:
            job_title (str): The job title being searched
            location (str): The location being searched
            job_data (dict): Prepared job data for analysis
        
        Returns:
            str: The prompt for the AI model
        """
        if job_data['total_jobs'] == 0:
            return f"""
            Analyze the job market for "{job_title}" positions in "{location}".
            
            No jobs were found for this search. Please provide insights on:
            1. Possible reasons for the lack of results
            2. Alternative job titles or locations to consider
            3. Market trends that might explain this situation
            4. Recommendations for recruiters
            
            Keep the response concise and actionable for recruiters.
            """
        
        # Calculate average salary if available
        salary_info = ""
        if job_data['salary_ranges']:
            valid_salaries = [s for s in job_data['salary_ranges'] if s['min'] or s['max']]
            if valid_salaries:
                avg_min = sum(s['min'] for s in valid_salaries if s['min']) / len([s for s in valid_salaries if s['min']])
                avg_max = sum(s['max'] for s in valid_salaries if s['max']) / len([s for s in valid_salaries if s['max']])
                salary_info = f"Average salary range: £{avg_min:,.0f} - £{avg_max:,.0f}"
        
        prompt = f"""
        Analyze the job market for "{job_title}" positions in "{location}" based on the following data:
        
        Total jobs found: {job_data['total_jobs']}
        Top hiring companies: {', '.join(job_data['companies'][:5]) if job_data['companies'] else 'Various companies'}
        Contract types available: {', '.join(job_data['contract_types']) if job_data['contract_types'] else 'Mixed'}
        {salary_info}
        
        Provide a concise market summary covering:
        1. Market demand and competition level
        2. Salary expectations and trends
        3. Key skills or qualifications in demand
        4. Actionable insights for recruiters
        
        Keep the response under 400 words and focus on practical insights for recruitment professionals.
        """
        
        return prompt
    
    def generate_job_description_summary(self, job_description):
        """
        Generate a concise summary of a job description.
        
        Args:
            job_description (str): The full job description
        
        Returns:
            str: Summarized job description
        """
        if not all([self.endpoint, self.api_key]):
            return "AI summary service not available."
        
        try:
            prompt = f"""
            Summarize this job description in 2-3 sentences, highlighting the key responsibilities and requirements:
            
            {job_description[:1000]}  # Limit input length
            """
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes job descriptions concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.5
            }
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Check if response content type is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"Azure AI returned non-JSON response for job description summary. Content-Type: {content_type}")
                return "Summary not available due to API response format error."
            
            try:
                result = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response from Azure AI for job description: {str(e)}")
                return "Summary not available due to response parsing error."
            
            # Ensure result is a dictionary and has expected structure
            if not isinstance(result, dict) or 'choices' not in result:
                logger.error(f"Azure AI returned unexpected response structure for job description: {type(result)}")
                return "Summary not available due to unexpected response format."
            
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize job description: {str(e)}")
            return "Summary not available."