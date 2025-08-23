#!/bin/bash

# Job Sight Monitoring Runner Script
# This script sets up and runs the monitoring system

echo "🔍 Starting Job Sight Monitoring System..."

# Check if we're in the right directory
if [ ! -f "monitor.py" ]; then
    echo "❌ Error: Please run this script from the monitoring directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DO_TOKEN" ]; then
    echo "❌ Error: DO_TOKEN environment variable is required"
    echo "Please set your DigitalOcean API token:"
    echo "export DO_TOKEN=your_token_here"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
echo "📁 Creating monitoring directories..."
mkdir -p data charts templates

# Run the monitoring script
echo "🚀 Starting monitoring..."
python3 monitor.py

echo "✅ Monitoring completed!"
