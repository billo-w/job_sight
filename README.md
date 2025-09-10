# Job Sight

A Flask web application that helps users search for jobs and get AI-powered insights about the job market.

## What This Application Does

Job Sight allows users to:
- **Search for jobs** - Find job opportunities using real job posting data
- **Get AI market insights** - Receive intelligent analysis about job market trends and salary information
- **Save jobs** - Bookmark interesting positions for later review
- **Manage accounts** - Register and login to save personal job searches

## How It Works

1. **Job Search**: Users enter job titles and locations to search real job postings from the Adzuna Jobs API
2. **AI Analysis**: The app uses Azure AI to provide market insights, salary trends, and job market analysis
3. **Personal Dashboard**: Users can save jobs they're interested in and access them later
4. **Simple Interface**: Clean, responsive design that works on desktop and mobile

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** - Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   ADZUNA_APP_ID=your-adzuna-app-id
   ADZUNA_API_KEY=your-adzuna-api-key
   AZURE_AI_ENDPOINT=your-azure-ai-endpoint
   AZURE_AI_KEY=your-azure-ai-key
   ```

3. **Initialize the database**:
   ```bash
   python -c "from app import db; db.create_all()"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

Visit `http://localhost:5000` to use the application.

## API Keys Needed

- **Adzuna API**: Get free API keys from [developer.adzuna.com](https://developer.adzuna.com/)
- **Azure AI**: Create an AI resource at [oai.azure.com](https://oai.azure.com/)

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL (for user accounts and saved jobs)
- **External APIs**: Adzuna Jobs API, Azure AI
- **Frontend**: HTML/CSS with responsive design