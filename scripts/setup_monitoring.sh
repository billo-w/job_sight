#!/bin/bash

# Job Sight Monitoring Setup Script
# This script helps set up and test the comprehensive monitoring system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check application health
check_health() {
    local app_url=$1
    print_status "Checking application health at $app_url/health"
    
    if curl -f -s "$app_url/health" >/dev/null; then
        print_success "Application health check passed"
        return 0
    else
        print_error "Application health check failed"
        return 1
    fi
}

# Function to check metrics endpoint
check_metrics() {
    local app_url=$1
    print_status "Checking metrics endpoint at $app_url/metrics"
    
    if curl -f -s "$app_url/metrics" | grep -q "http_requests_total"; then
        print_success "Metrics endpoint is working correctly"
        return 0
    else
        print_error "Metrics endpoint is not working correctly"
        return 1
    fi
}

# Function to generate test traffic
generate_test_traffic() {
    local app_url=$1
    print_status "Generating test traffic to create metrics"
    
    # Test basic endpoints
    curl -s "$app_url/" >/dev/null
    curl -s "$app_url/health" >/dev/null
    curl -s "$app_url/metrics" >/dev/null
    
    print_success "Test traffic generated"
}

# Function to validate monitoring configuration
validate_monitoring_config() {
    print_status "Validating monitoring configuration"
    
    # Check if required files exist
    local required_files=(
        "app.py"
        "requirements.txt"
        "terraform/main.tf"
        "terraform/monitoring.tf"
        "monitoring/dashboard.json"
        "monitoring/README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_success "Found $file"
        else
            print_error "Missing $file"
            return 1
        fi
    done
    
    # Check if monitoring dependencies are in requirements.txt
    if grep -q "prometheus-client" requirements.txt && \
       grep -q "structlog" requirements.txt && \
       grep -q "python-json-logger" requirements.txt; then
        print_success "Monitoring dependencies found in requirements.txt"
    else
        print_error "Monitoring dependencies missing from requirements.txt"
        return 1
    fi
    
    print_success "Monitoring configuration validation passed"
}

# Function to test logging
test_logging() {
    local app_url=$1
    print_status "Testing structured logging"
    
    # Make a request and check if logs are generated
    curl -s "$app_url/" >/dev/null
    
    print_success "Logging test completed (check application logs for structured output)"
}

# Function to check DigitalOcean App Platform status
check_do_app_status() {
    if command_exists doctl; then
        print_status "Checking DigitalOcean App Platform status"
        
        # Get app status
        local app_status=$(doctl apps list --format ID,Spec.Name,Spec.Services.0.Source.Image.Tag,Status 2>/dev/null | grep "job-sight" || echo "")
        
        if [[ -n "$app_status" ]]; then
            print_success "Found Job Sight app in DigitalOcean: $app_status"
        else
            print_warning "Job Sight app not found in DigitalOcean (may not be deployed yet)"
        fi
    else
        print_warning "doctl not found - skipping DigitalOcean status check"
    fi
}

# Function to display monitoring dashboard information
show_dashboard_info() {
    print_status "Monitoring Dashboard Information"
    echo ""
    echo "Dashboard Configuration:"
    echo "  - File: monitoring/dashboard.json"
    echo "  - Panels: 10 comprehensive monitoring panels"
    echo "  - Metrics: HTTP requests, response times, business metrics"
    echo "  - Refresh: 30 seconds"
    echo ""
    echo "Available Endpoints:"
    echo "  - Health Check: /health"
    echo "  - Metrics: /metrics"
    echo "  - Prometheus Format: Compatible with Grafana, Prometheus"
    echo ""
    echo "Custom Metrics:"
    echo "  - http_requests_total: Request counts by method/endpoint/status"
    echo "  - http_request_duration_seconds: Response time distribution"
    echo "  - job_searches_total: Job search patterns by location/title"
    echo "  - api_calls_total: API call success/failure rates"
    echo "  - database_operations_total: Database operation counts"
    echo "  - active_users: Current active user count"
}

# Function to provide setup instructions
show_setup_instructions() {
    print_status "Monitoring Setup Instructions"
    echo ""
    echo "1. Deploy the application:"
    echo "   - Push to main branch to trigger CI/CD pipeline"
    echo "   - Terraform will automatically apply monitoring configuration"
    echo ""
    echo "2. Configure external monitoring tools (optional):"
    echo "   - Grafana: Import monitoring/dashboard.json"
    echo "   - Prometheus: Scrape /metrics endpoint"
    echo "   - Better Stack: Configure log forwarding"
    echo ""
    echo "3. Set up alerting:"
    echo "   - Configure email notifications in Terraform variables"
    echo "   - Set up Slack webhook for real-time alerts"
    echo "   - Adjust alert thresholds as needed"
    echo ""
    echo "4. Test monitoring:"
    echo "   - Run this script with your app URL"
    echo "   - Verify metrics are being collected"
    echo "   - Check alerting is working"
    echo ""
    echo "5. Monitor and optimize:"
    echo "   - Review dashboard regularly"
    echo "   - Tune alert thresholds"
    echo "   - Add custom metrics as needed"
}

# Main script logic
main() {
    echo "=========================================="
    echo "Job Sight Monitoring Setup Script"
    echo "=========================================="
    echo ""
    
    # Check if app URL is provided
    if [[ $# -eq 0 ]]; then
        print_error "Please provide the application URL"
        echo "Usage: $0 <app_url>"
        echo "Example: $0 https://job-sight-app.ondigitalocean.app"
        echo ""
        show_setup_instructions
        exit 1
    fi
    
    local app_url=$1
    
    # Remove trailing slash if present
    app_url=${app_url%/}
    
    print_status "Starting monitoring setup for: $app_url"
    echo ""
    
    # Validate monitoring configuration
    validate_monitoring_config
    
    # Check application health
    if check_health "$app_url"; then
        # Test metrics endpoint
        check_metrics "$app_url"
        
        # Generate test traffic
        generate_test_traffic "$app_url"
        
        # Test logging
        test_logging "$app_url"
        
        # Check DigitalOcean status
        check_do_app_status
        
        echo ""
        print_success "Monitoring setup completed successfully!"
        echo ""
        show_dashboard_info
        
    else
        print_error "Application is not responding. Please ensure it's deployed and running."
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
