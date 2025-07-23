# Job Sight - Recruiter Job Search Platform

Job Sight is a powerful web application designed for recruiters to search for jobs, analyze market trends with AI-powered insights, and manage their recruitment pipeline efficiently.

## Features

- **🔍 Advanced Job Search**: Search thousands of live job postings using the Adzuna API
- **🤖 AI Market Insights**: Get intelligent market summaries powered by Azure AI Foundry (GPT-4o)
- **💾 Job Management**: Save and organize interesting job opportunities
- **👤 User Authentication**: Secure registration and login system
- **📊 Search History**: Track your search patterns and results
- **📱 Responsive Design**: Beautiful, mobile-friendly interface built with Tailwind CSS

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (Digital Ocean)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **APIs**: Adzuna Jobs API, Azure AI Foundry (GPT-4o)
- **Authentication**: Flask-Login
- **Database ORM**: SQLAlchemy
- **Migrations**: Flask-Migrate

## Prerequisites

- Python 3.8+
- PostgreSQL database (Digital Ocean)
- Adzuna API credentials
- Azure AI Foundry credentials

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job_sight
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ADZUNA_APP_ID=your_adzuna_app_id
   ADZUNA_APP_KEY=your_adzuna_app_key
   AZURE_AI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_AI_KEY=your_azure_ai_key
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## API Credentials Setup

### Adzuna API
1. Visit [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Create an account and register your application
3. Get your `app_id` and `app_key`
4. Add them to your `.env` file

### Azure AI Foundry
1. Create an Azure account and set up Azure AI Foundry
2. Deploy a GPT-4o model
3. Get your endpoint URL and API key
4. Add them to your `.env` file

## Digital Ocean PostgreSQL Setup

1. **Create a PostgreSQL database on Digital Ocean**
   - Log into your Digital Ocean account
   - Go to Databases and create a new PostgreSQL cluster
   - Note down the connection details

2. **Configure the connection**
   - Update the `DATABASE_URL` in your `.env` file
   - Format: `postgresql://username:password@host:port/database_name`

3. **Test the connection**
   ```bash
   flask db upgrade
   ```

## Project Structure

```
job_sight/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── forms.py              # WTForms for user input
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── services/
│   ├── adzuna_api.py    # Adzuna API integration
│   └── azure_ai.py     # Azure AI service
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── results.html     # Search results
│   ├── saved_jobs.html  # Saved jobs page
│   └── auth/
│       ├── login.html   # Login page
│       └── register.html # Registration page
└── migrations/          # Database migrations
```

## Usage

1. **Register an account** or log in if you already have one
2. **Search for jobs** by entering a job title and location
3. **View AI insights** at the top of search results for market analysis
4. **Save interesting jobs** by clicking the bookmark icon
5. **Manage saved jobs** from the "Saved Jobs" page
6. **Track your searches** in your profile

## Database Schema

### Users Table
- User authentication and profile information
- Relationships to saved jobs and search history

### Saved Jobs Table
- Stores job opportunities saved by users
- Includes job details, salary information, and save timestamp

### Search History Table
- Tracks user search patterns
- Useful for analytics and user experience improvements

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade if needed
flask db downgrade
```

### Adding New Features
1. Update models in `models.py` if database changes are needed
2. Create migration: `flask db migrate -m "Feature description"`
3. Update forms in `forms.py` for new user inputs
4. Add routes in `app.py`
5. Create/update templates in `templates/`

## Deployment

### Production Considerations
1. **Security**: Change the `SECRET_KEY` to a secure random value
2. **Database**: Ensure PostgreSQL is properly configured and secured
3. **Environment**: Set `FLASK_ENV=production`
4. **HTTPS**: Use SSL/TLS in production
5. **Monitoring**: Set up logging and monitoring

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Rate Limits

- **Adzuna API**: Check your plan limits
- **Azure AI**: Monitor token usage and costs

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL credentials in `.env`
   - Check if the database server is accessible
   - Ensure `psycopg2-binary` is installed

2. **API Errors**
   - Verify API credentials are correct
   - Check API rate limits
   - Ensure internet connectivity

3. **Migration Issues**
   - Delete `migrations/` folder and reinitialize if needed
   - Check database permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please create an issue in the repository.