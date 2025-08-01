# Use official Python image as base with latest security patches
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    && apk upgrade

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools>=78.1.1 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN adduser -D -s /bin/sh app && chown -R app:app /app
USER app

# Tell Flask which app to load
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

# Expose port and run
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]