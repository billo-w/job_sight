# Import the requests library for making HTTP API calls to external AI services
# This is the standard Python library for HTTP client operations
import requests
# Import Flask's current_app to access application configuration in a thread-safe manner
# current_app provides access to the Flask application context and configuration
from flask import current_app
# Import logging module for structured application logging and monitoring
# Essential for DevOps observability and debugging in production AI systems
import logging
# Import json module for JSON data manipulation and formatting
# Required for constructing AI API payloads and handling responses
import json

# Create a logger instance specific to this module for traceability and debugging
# Using __name__ ensures log messages are properly namespaced for this AI service
# This enables granular log filtering and monitoring in production AI systems
logger = logging.getLogger(__name__)

class AzureAIService:
    """
    Service class for interacting with Azure AI Foundry GPT-4o model.
    
    This class implements AI service integration patterns and demonstrates:
    - Secure API key management for AI services
    - Prompt engineering and template management
    - AI response validation and error handling
    - Token management and cost optimization
    - Structured logging for AI service monitoring
    - Graceful degradation when AI services are unavailable
    - Data preparation and transformation for AI analysis
    """
    
    def __init__(self):
        """
        Initialize the Azure AI service with configuration from Flask app context.
        
        DevOps Pattern: Secure AI Service Configuration
        - AI endpoints and keys are injected from environment-specific configuration
        - No hardcoded AI credentials, supporting different environments
        - Model configuration allows for easy AI model upgrades
        - Fail-fast pattern for missing AI credentials with graceful degradation
        """
        # Retrieve Azure AI endpoint URL from Flask configuration
        # This supports different AI environments (dev/staging/prod)
        # Endpoint URL determines which Azure AI instance to use
        self.endpoint = current_app.config.get('AZURE_AI_ENDPOINT')
        
        # Retrieve Azure AI API key from Flask configuration
        # Sensitive AI credentials are managed through configuration, not hardcoded
        # In production, this should come from secure secret management systems
        self.api_key = current_app.config.get('AZURE_AI_KEY')
        
        # Retrieve AI model name from configuration with default fallback
        # This allows for easy model upgrades and A/B testing
        # Default to 'gpt-4o' which provides good balance of capability and cost
        self.model = current_app.config.get('AZURE_AI_MODEL', 'gpt-4o')
        
        # Validate that required AI credentials are present at initialization
        # Defensive programming: check AI dependencies early to fail fast
        # This prevents runtime errors and enables proactive AI service monitoring
        if not all([self.endpoint, self.api_key]):
            # Log warning for monitoring systems to detect AI configuration issues
            # This enables proactive alerting on missing AI credentials
            # Warning level allows service to continue but alerts operations team
            logger.warning("Azure AI credentials not configured")
    
    def generate_job_market_summary(self, job_title, location, job_results):
        """
        Generate an AI-powered summary of the job market for a specific role and location.
        
        This method demonstrates AI service integration patterns:
        - Circuit breaker pattern for AI service availability
        - Data preparation and feature extraction for AI analysis
        - Prompt engineering with structured templates
        - Token management and cost optimization
        - AI response validation and error handling
        - Structured AI service monitoring and logging
        
        Args:
            job_title (str): The job title being searched
            location (str): The location being searched
            job_results (list): List of job results from the search
        
        Returns:
            dict: Contains the AI-generated summary text and metadata
        """
        # Circuit breaker pattern: fail fast if AI credentials are not configured
        # Prevents unnecessary AI API calls when service is not properly configured
        # This pattern improves system resilience and reduces AI service costs
        if not all([self.endpoint, self.api_key]):
            # Return standardized error response with user-friendly message
            # Consistent error format enables better error handling in calling code
            # This supports automated error detection and AI service monitoring
            return {
                'summary': 'AI summary service is not configured. Please check your Azure AI credentials.',
                'error': True
            }
        
        # Comprehensive try-catch block for robust AI service error handling
        # Different exception types are handled appropriately for better debugging
        # This enables proper error categorization for AI service monitoring
        try:
            # Prepare job data for AI analysis using helper method
            # Data preparation is crucial for effective AI prompt engineering
            # This step extracts relevant features and reduces token usage
            job_data = self._prepare_job_data(job_results)
            
            # Create the prompt for GPT-4o using structured template
            # Prompt engineering is critical for AI service effectiveness
            # This method encapsulates prompt logic for maintainability
            prompt = self._create_market_analysis_prompt(job_title, location, job_data)
            
            # Prepare the request payload for Azure OpenAI API
            # Structured payload construction ensures consistent AI interactions
            # This pattern supports prompt versioning and A/B testing
            payload = {
                # Messages array following OpenAI chat completion format
                "messages": [
                    {
                        # System message defines AI assistant role and behavior
                        # This prompt engineering technique ensures consistent AI responses
                        "role": "system",
                        # Detailed system prompt for recruitment analyst persona
                        # Specific instructions improve AI response quality and consistency
                        "content": "You are an expert recruitment analyst providing insights about job markets. Provide concise, actionable insights for recruiters. Format your response as plain text with clear paragraphs, not markdown."
                    },
                    {
                        # User message contains the actual analysis request
                        # This separation allows for role-based prompt engineering
                        "role": "user",
                        # Dynamic prompt content based on job search data
                        "content": prompt
                    }
                ],
                # Token limit for cost control and response length management
                # 500 tokens provides good balance between detail and cost
                "max_tokens": 500,
                # Temperature controls AI creativity vs consistency
                # 0.7 provides good balance for analytical content
                "temperature": 0.7
            }
            
            # Prepare HTTP headers for Azure AI API authentication
            # Proper header construction is essential for AI service integration
            headers = {
                # Content-Type header for JSON payload
                "Content-Type": "application/json",
                # Azure-specific API key header for authentication
                # Different from OpenAI's Authorization header format
                "api-key": self.api_key
            }
            
            # Make the API call to Azure OpenAI with extended timeout
            # 30-second timeout accommodates AI processing time
            # POST method with JSON payload for chat completion
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            # Raise exception for HTTP error status codes (4xx, 5xx)
            # This converts HTTP errors into Python exceptions for consistent error handling
            response.raise_for_status()
            
            # Validate response content type to ensure we received JSON
            # Content-Type validation prevents parsing errors from unexpected AI responses
            # This defensive programming pattern improves AI service reliability
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                # Log error with specific details for AI service debugging and monitoring
                # Include content-type for troubleshooting AI API changes or issues
                logger.error(f"Azure AI returned non-JSON response. Content-Type: {content_type}")
                # Return standardized error response for consistent AI error handling
                return {
                    'summary': 'Unable to generate market summary due to API response format error.',
                    'error': True
                }
            
            # Parse JSON response with error handling for malformed AI responses
            # Separate try-catch for JSON parsing provides specific AI error handling
            # This enables differentiation between network and AI response parsing errors
            try:
                # Attempt to parse the AI response body as JSON
                # This may fail if the AI service returns malformed JSON
                result = response.json()
            except ValueError as e:
                # Log JSON parsing errors with exception details for AI debugging
                # Include the actual error message for AI service troubleshooting
                logger.error(f"Failed to parse JSON response from Azure AI: {str(e)}")
                # Return user-friendly error message while logging technical details
                return {
                    'summary': 'Unable to generate market summary due to response parsing error.',
                    'error': True
                }
            
            # Validate that parsed AI response has expected OpenAI structure
            # Type and structure validation prevents runtime errors from unexpected AI responses
            # This defensive programming pattern improves AI service stability
            if not isinstance(result, dict) or 'choices' not in result:
                # Log unexpected AI response structure for monitoring and debugging
                # Include actual type information for AI service troubleshooting
                logger.error(f"Azure AI returned unexpected response structure: {type(result)}")
                # Return standardized error response for AI service failures
                return {
                    'summary': 'Unable to generate market summary due to unexpected response format.',
                    'error': True
                }
            
            # Extract AI-generated content from OpenAI response structure
            # Navigate the nested response structure to get the actual AI text
            # .strip() removes any leading/trailing whitespace from AI response
            summary = result['choices'][0]['message']['content'].strip()
            
            # Return standardized success response with AI-generated content and metadata
            # Consistent response format enables reliable client-side processing
            # This contract-based approach supports AI service versioning and evolution
            return {
                'summary': summary,                    # AI-generated market analysis text
                'error': False,                       # Success indicator
                'job_count': len(job_results),        # Number of jobs analyzed
                'location': location,                 # Location analyzed
                'job_title': job_title               # Job title analyzed
            }
            
        # Catch-all exception handler for any AI service errors
        # This ensures the method never raises unhandled exceptions
        # Critical for AI service reliability and user experience
        except Exception as e:
            # Log all AI service errors for debugging and monitoring
            # Include method context for AI service troubleshooting
            logger.error(f"Azure AI API request failed: {str(e)}")
            # Return user-friendly error message with optional technical details
            # This balances user experience with operational AI service visibility
            return {
                'summary': f'Unable to generate market summary at this time. Please try again later.',
                'error': True,
                'error_message': str(e)
            }
    
    def _prepare_job_data(self, job_results):
        """
        Prepare job data for AI analysis by extracting key information.
        
        This method demonstrates data preparation patterns for AI services:
        - Feature extraction from raw job data
        - Data aggregation and summarization
        - Token optimization through data reduction
        - Safe data handling with type validation
        - Deduplication and data quality improvement
        
        Args:
            job_results (list): List of job results from search
        
        Returns:
            dict: Summarized job data optimized for AI analysis
        """
        # Handle empty job results gracefully
        # Early return pattern for edge cases in AI data preparation
        # This prevents AI processing errors and reduces unnecessary token usage
        if not job_results:
            # Return structured empty data that AI can still analyze
            # This enables AI to provide insights about lack of results
            return {
                'total_jobs': 0,
                'companies': [],
                'salary_ranges': [],
                'contract_types': [],
                'locations': []
            }
        
        # Initialize data collection lists for feature extraction
        # Separate lists enable efficient data aggregation and deduplication
        # This pattern supports scalable data processing for AI analysis
        companies = []
        salary_ranges = []
        contract_types = []
        locations = []
        
        # Process job results with data limitation for token optimization
        # Limit to first 20 jobs to control AI token usage and costs
        # This balances data completeness with AI service efficiency
        for job in job_results[:20]:  # Limit to first 20 jobs for analysis
            # Validate job data type before processing
            # Type checking prevents runtime errors in AI data preparation
            # This defensive programming pattern improves AI service reliability
            if not isinstance(job, dict):
                # Log warning about invalid job data for monitoring
                # Include actual data type and value for debugging
                logger.warning(f"Skipping invalid job data: {type(job)} - {job}")
                # Skip invalid data and continue processing
                # This graceful error handling maintains AI service availability
                continue
                
            # Extract company names for market analysis
            # Company data helps AI identify hiring trends and market leaders
            # Safe dictionary access prevents KeyError exceptions
            if job.get('company'):
                # Add company name to list for aggregation
                companies.append(job['company'])
            
            # Extract salary information for compensation analysis
            # Salary data enables AI to provide market rate insights
            # Check for either minimum or maximum salary data
            if job.get('salary_min') or job.get('salary_max'):
                # Create structured salary information for AI analysis
                # This format preserves data quality indicators
                salary_info = {
                    'min': job.get('salary_min'),                    # Minimum salary value
                    'max': job.get('salary_max'),                    # Maximum salary value
                    'is_predicted': job.get('salary_is_predicted', False)  # Data quality flag
                }
                # Add salary information to list for aggregation
                salary_ranges.append(salary_info)
            
            # Extract contract types for employment analysis
            # Contract type data helps AI identify employment trends
            # Safe dictionary access with existence check
            if job.get('contract_type'):
                # Add contract type to list for aggregation
                contract_types.append(job['contract_type'])
            
            # Extract locations for geographic analysis
            # Location data enables AI to provide regional insights
            # Safe dictionary access with existence check
            if job.get('location'):
                # Add location to list for aggregation
                locations.append(job['location'])
        
        # Return aggregated and deduplicated data optimized for AI analysis
        # This structured format enables effective AI prompt engineering
        # Data reduction techniques optimize token usage and AI costs
        return {
            # Total job count for market size analysis
            'total_jobs': len(job_results),
            # Top 10 unique companies to identify major employers
            # Deduplication and limiting reduces token usage while preserving insights
            'companies': list(set(companies))[:10],  # Top 10 unique companies
            # All salary ranges for compensation analysis
            # Preserve all salary data for accurate market analysis
            'salary_ranges': salary_ranges,
            # Unique contract types for employment pattern analysis
            # Deduplication provides clean data for AI analysis
            'contract_types': list(set(contract_types)),
            # Top 5 unique locations for geographic analysis
            # Limiting locations reduces token usage while preserving regional insights
            'locations': list(set(locations))[:5]  # Top 5 unique locations
        }
    
    def _create_market_analysis_prompt(self, job_title, location, job_data):
        """
        Create a structured prompt for the AI model to analyze the job market.
        
        This method demonstrates prompt engineering best practices:
        - Conditional prompt generation based on data availability
        - Structured prompt templates for consistent AI responses
        - Data integration into natural language prompts
        - Clear instruction formatting for AI comprehension
        - Token optimization through efficient prompt construction
        
        Args:
            job_title (str): The job title being searched
            location (str): The location being searched
            job_data (dict): Prepared job data for analysis
        
        Returns:
            str: The structured prompt for the AI model
        """
        # Handle case where no jobs were found
        # Special prompt template for zero-result scenarios
        # This enables AI to provide valuable insights even without job data
        if job_data['total_jobs'] == 0:
            # Return structured prompt for no-results analysis
            # This prompt engineering technique guides AI to provide actionable insights
            return f"""
            Analyze the job market for "{job_title}" positions in "{location}".
            
            No jobs were found for this search. Please provide insights on:
            1. Possible reasons for the lack of results
            2. Alternative job titles or locations to consider
            3. Market trends that might explain this situation
            4. Recommendations for recruiters
            
            Keep the response concise and actionable for recruiters.
            """
        
        # Calculate average salary information for market analysis
        # Salary aggregation provides valuable compensation insights for AI
        # This data preparation enhances AI analysis quality
        salary_info = ""
        # Check if salary data is available for analysis
        if job_data['salary_ranges']:
            # Filter out salary entries without actual values
            # This data cleaning improves AI analysis accuracy
            valid_salaries = [s for s in job_data['salary_ranges'] if s['min'] or s['max']]
            # Process salary data if valid entries exist
            if valid_salaries:
                # Calculate average minimum salary from available data
                # List comprehension with filtering for efficient data processing
                avg_min = sum(s['min'] for s in valid_salaries if s['min']) / len([s for s in valid_salaries if s['min']])
                # Calculate average maximum salary from available data
                # Separate calculation handles cases where min/max availability differs
                avg_max = sum(s['max'] for s in valid_salaries if s['max']) / len([s for s in valid_salaries if s['max']])
                # Format salary information for AI prompt inclusion
                # Structured format helps AI understand compensation context
                salary_info = f"Average salary range: £{avg_min:,.0f} - £{avg_max:,.0f}"
        
        # Construct comprehensive market analysis prompt
        # This structured template ensures consistent AI analysis across requests
        # F-string formatting enables dynamic data integration
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
        
        # Return the constructed prompt for AI processing
        # This structured approach enables consistent AI analysis
        return prompt
    
    def generate_job_description_summary(self, job_description):
        """
        Generate a concise summary of a job description using AI.
        
        This method demonstrates AI text summarization patterns:
        - Input length limitation for token management
        - Specialized prompt engineering for summarization
        - Different AI parameters for summarization tasks
        - Consistent error handling for AI services
        - Cost optimization through targeted AI usage
        
        Args:
            job_description (str): The full job description text
        
        Returns:
            str: AI-generated concise summary of the job description
        """
        # Circuit breaker pattern: fail fast if AI credentials are not configured
        # Prevents unnecessary AI API calls when service is not properly configured
        # This pattern improves system resilience and reduces AI service costs
        if not all([self.endpoint, self.api_key]):
            # Return simple fallback message for missing AI configuration
            # This graceful degradation maintains application functionality
            return "AI summary service not available."
        
        # Comprehensive error handling for AI summarization service
        # This pattern ensures the method never raises unhandled exceptions
        try:
            # Create summarization prompt with input length limitation
            # Limiting input to 1000 characters controls token usage and costs
            # This prompt engineering technique focuses AI on key content
            prompt = f"""
            Summarize this job description in 2-3 sentences, highlighting the key responsibilities and requirements:
            
            {job_description[:1000]}  # Limit input length
            """
            
            # Prepare AI request payload for summarization task
            # Different parameters optimize AI for summarization vs analysis
            payload = {
                # Messages array following OpenAI chat completion format
                "messages": [
                    {
                        # System message defines AI assistant role for summarization
                        # Specialized prompt for summarization tasks
                        "role": "system",
                        # Concise system prompt for job description summarization
                        "content": "You are a helpful assistant that summarizes job descriptions concisely."
                    },
                    {
                        # User message contains the summarization request
                        "role": "user",
                        # Dynamic prompt content with job description text
                        "content": prompt
                    }
                ],
                # Lower token limit for summarization tasks
                # 150 tokens sufficient for 2-3 sentence summaries
                "max_tokens": 150,
                # Lower temperature for more focused, consistent summaries
                # 0.5 provides good balance for factual summarization
                "temperature": 0.5
            }
            
            # Prepare HTTP headers for Azure AI API authentication
            # Same header pattern as market analysis for consistency
            headers = {
                # Content-Type header for JSON payload
                "Content-Type": "application/json",
                # Azure-specific API key header for authentication
                "api-key": self.api_key
            }
            
            # Make the API call to Azure OpenAI for summarization
            # Same timeout and error handling pattern for consistency
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            # Raise exception for HTTP error status codes (4xx, 5xx)
            response.raise_for_status()
            
            # Validate response content type for AI summarization response
            # Same validation pattern as market analysis for consistency
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                # Log error with specific context for AI summarization debugging
                logger.error(f"Azure AI returned non-JSON response for job description summary. Content-Type: {content_type}")
                # Return fallback message for content type errors
                return "Summary not available due to API response format error."
            
            # Parse JSON response with error handling for AI summarization
            # Same parsing pattern as market analysis for consistency
            try:
                # Attempt to parse the AI summarization response as JSON
                result = response.json()
            except ValueError as e:
                # Log JSON parsing errors for AI summarization debugging
                logger.error(f"Failed to parse JSON response from Azure AI for job description: {str(e)}")
                # Return fallback message for parsing errors
                return "Summary not available due to response parsing error."
            
            # Validate AI response structure for summarization
            # Same validation pattern as market analysis for consistency
            if not isinstance(result, dict) or 'choices' not in result:
                # Log unexpected AI response structure for summarization debugging
                logger.error(f"Azure AI returned unexpected response structure for job description: {type(result)}")
                # Return fallback message for structure errors
                return "Summary not available due to unexpected response format."
            
            # Extract and return AI-generated summary text
            # Navigate OpenAI response structure and clean the text
            # .strip() removes any leading/trailing whitespace from AI response
            return result['choices'][0]['message']['content'].strip()
            
        # Catch-all exception handler for AI summarization errors
        # This ensures the method never raises unhandled exceptions
        except Exception as e:
            # Log all AI summarization errors for debugging and monitoring
            logger.error(f"Failed to summarize job description: {str(e)}")
            # Return simple fallback message for any errors
            # This graceful degradation maintains application functionality
            return "Summary not available."