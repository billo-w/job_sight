#!/bin/bash

# Job Sight Monitoring Setup Script
# This script helps you set up the monitoring system

echo "🔧 Setting up Job Sight Monitoring System..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "monitor.py" ]; then
    echo "❌ Error: Please run this script from the monitoring directory"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if DO_TOKEN is set
if [ -z "$DO_TOKEN" ]; then
    echo "⚠️  Warning: DO_TOKEN environment variable is not set"
    echo "You'll need to set it before running the monitoring system:"
    echo "export DO_TOKEN=your_digitalocean_api_token"
    echo ""
    echo "To get your DigitalOcean API token:"
    echo "1. Go to https://cloud.digitalocean.com/account/api/tokens"
    echo "2. Generate a new token with read permissions"
    echo "3. Copy the token and set it as DO_TOKEN"
    echo ""
else
    echo "✅ DO_TOKEN environment variable is set"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p data charts templates

# Make scripts executable
chmod +x run_monitoring.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your environment variables:"
echo "   export DO_TOKEN=your_token"
echo "   export APP_URL=your_app_url"
echo "   export APP_ID=your_app_id"
echo ""
echo "2. Get your app information:"
echo "   python3 get_app_info.py"
echo ""
echo "3. Run monitoring:"
echo "   python3 monitor.py"
echo ""
echo "4. Start web dashboard:"
echo "   python3 dashboard.py"
echo ""
echo "5. Or use the convenience script:"
echo "   ./run_monitoring.sh"
echo ""
echo "📚 For more information, see README.md"
