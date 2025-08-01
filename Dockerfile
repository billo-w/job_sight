# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Tell Flask which app to load
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

# Expose port and run
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]