# Database Migrations

This directory contains Flask-Migrate migration files for the Job Sight application.

## Setup

1. Initialize the migration repository (only needed once):
```bash
flask db init
```

2. Create a new migration after model changes:
```bash
flask db migrate -m "Description of changes"
```

3. Apply migrations to the database:
```bash
flask db upgrade
```

## PostgreSQL Setup

To connect to your Digital Ocean PostgreSQL database:

1. Copy `.env.example` to `.env`
2. Update the `DATABASE_URL` with your Digital Ocean PostgreSQL credentials:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

3. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

4. Run migrations:
   ```bash
   flask db upgrade
   ```

## Database Schema

The application uses the following tables:

### users
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- first_name
- last_name
- created_at
- updated_at

### saved_jobs
- id (Primary Key)
- user_id (Foreign Key to users.id)
- job_id (Adzuna job ID)
- job_title
- company
- location
- salary_min
- salary_max
- job_url
- description
- saved_at

### search_history
- id (Primary Key)
- user_id (Foreign Key to users.id)
- job_title
- location
- search_date
- results_count