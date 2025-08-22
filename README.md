# Job Sight - Simplified Job Search Application

A simplified Flask-based job search application that helps recruiters find jobs and get AI-powered market insights. This application has been streamlined for easier understanding and maintenance while keeping core functionality.

## Features

- **Job Search**: Search for jobs using the Adzuna API
- **AI Market Analysis**: Get AI-powered insights about job markets using Azure AI
- **User Authentication**: Register, login, and manage user accounts
- **Save Jobs**: Save interesting job opportunities for later reference
- **Simple Interface**: Clean, modern UI built with custom CSS

## Core Functionality

### What's Included
- User registration and login
- Job search with real-time results
- AI-powered market analysis
- Save/unsave job functionality
- Responsive design with custom CSS
- Simple, clean codebase structure

### What's Simplified
- **Single File Structure**: Everything is in `app.py` - no separate files for models, forms, config, or services
- **Custom CSS**: Simple, clean styling without external CSS frameworks
- **Minimal Dependencies**: Only essential packages required
- **Easy to Understand**: Straightforward code that's easy to explain during assessments

## File Structure

```
job_sight/
├── app.py                 # Main application file (everything in one place)
├── static/
│   └── styles.css         # Custom CSS styles
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── results.html       # Job search results
│   ├── profile.html       # User profile
│   ├── saved_jobs.html    # Saved jobs page
│   ├── auth/
│   │   ├── login.html     # Login page
│   │   └── register.html  # Registration page
│   ├── 404.html           # Error page
│   └── 500.html           # Server error page
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # Environment variables (create this)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///job_sight.db
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_API_KEY=your-adzuna-api-key
AZURE_AI_ENDPOINT=your-azure-ai-endpoint
AZURE_AI_KEY=your-azure-ai-key
```

### 3. Initialize Database
```bash
python3 -c "from app import db; db.create_all(); print('Database created successfully')"
```

### 4. Run the Application
```bash
python3 app.py
```

The application will be available at `http://localhost:5000`

## API Keys Required

### Adzuna API (for job search)
1. Go to [Adzuna API](https://developer.adzuna.com/)
2. Register for a free account
3. Get your App ID and API Key
4. Add them to your `.env` file

### Azure AI (for market analysis)
1. Go to [Azure AI Studio](https://oai.azure.com/)
2. Create a new deployment
3. Get your endpoint and API key
4. Add them to your `.env` file

## Key Features Explained

### 1. User Authentication
- Simple registration and login system
- Password hashing for security
- Session management with Flask-Login

### 2. Job Search
- Integration with Adzuna Jobs API
- Real-time job results
- Pagination support
- Search by job title and location

### 3. AI Market Analysis
- Uses Azure AI (GPT-4o) for market insights
- Analyzes job market trends
- Provides salary and demand insights
- Summarizes market conditions

### 4. Save Jobs
- Save interesting job opportunities
- View saved jobs in a dedicated page
- Remove jobs from saved list
- Simple bookmark functionality

## Security Features

- Password hashing with Werkzeug
- CSRF protection
- Secure session management
- Input validation and sanitization
- Environment variable configuration

## Assessment-Ready Features

This simplified version is perfect for assessments because:

1. **Easy to Explain**: Single file structure makes it easy to walk through the code
2. **Clear Functionality**: Each feature is straightforward and well-documented
3. **Minimal Dependencies**: Only essential packages, easy to understand
4. **Custom CSS**: No complex CSS frameworks to explain
5. **Core Features**: Focuses on the essential functionality you need to demonstrate

## Troubleshooting

### Common Issues

1. **Database Errors**: Run the database initialization command
2. **API Errors**: Check your API keys in the `.env` file
3. **Import Errors**: Make sure all dependencies are installed

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your API keys are correct
3. Ensure all dependencies are installed
4. Check that the database file is created

## Deployment

This application can be deployed to:
- Heroku
- Railway
- Render
- Any platform that supports Python Flask applications

Make sure to set the environment variables in your deployment platform.

## License

This project is for educational and assessment purposes.