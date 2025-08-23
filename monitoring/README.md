# Job Sight Monitoring System

A simple and effective monitoring solution for the Job Sight application using DigitalOcean's API to create custom visualizations and track application performance.

## Features

- **Real-time Application Monitoring**: Monitor CPU, memory, and request metrics
- **Health Checks**: Automated health endpoint monitoring
- **Custom Visualizations**: Generate beautiful charts and dashboards
- **Web Dashboard**: Simple web interface to view monitoring data
- **Automated Reporting**: Generate JSON reports with metrics summaries
- **Log Management**: Collect and analyze application logs

## Quick Start

### 1. Set Environment Variables

```bash
export DO_TOKEN="your_digitalocean_api_token"
export APP_URL="https://your-app-url.com"
export APP_ID="your_app_id"
```

### 2. Install Dependencies

```bash
cd monitoring
pip3 install -r requirements.txt
```

### 3. Run Monitoring

```bash
# Run once
python3 monitor.py

# Or use the convenience script
./run_monitoring.sh
```

### 4. Start Web Dashboard

```bash
python3 dashboard.py
```

Then visit `http://localhost:5001` to view the monitoring dashboard.

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DO_TOKEN` | DigitalOcean API token | Yes |
| `APP_URL` | Your application URL | No (for health checks) |
| `APP_ID` | DigitalOcean App ID | No (for metrics) |

### Getting Your DigitalOcean App ID

1. Go to your DigitalOcean App Platform dashboard
2. Select your Job Sight app
3. The App ID is in the URL: `https://cloud.digitalocean.com/apps/{APP_ID}`

## Monitoring Components

### 1. Monitor Script (`monitor.py`)

The main monitoring script that:
- Fetches metrics from DigitalOcean API
- Performs health checks on your application
- Generates custom visualizations
- Creates JSON reports
- Logs all activities

### 2. Web Dashboard (`dashboard.py`)

A Flask web application that provides:
- Real-time status display
- Interactive charts
- Manual refresh capabilities
- Mobile-responsive design

### 3. Visualizations

The system creates custom charts showing:
- CPU usage over time
- Memory usage trends
- Request count analysis
- Application health status

## File Structure

```
monitoring/
├── monitor.py              # Main monitoring script
├── dashboard.py            # Web dashboard
├── requirements.txt        # Python dependencies
├── run_monitoring.sh       # Convenience script
├── README.md              # This file
├── data/                  # Generated reports
├── charts/                # Generated visualizations
├── templates/             # Dashboard templates
└── app_monitor.log        # Monitoring logs
```

## Usage Examples

### Basic Monitoring

```bash
# Run a single monitoring cycle
python3 monitor.py
```

### Continuous Monitoring

```bash
# Run monitoring every 5 minutes
while true; do
    python3 monitor.py
    sleep 300
done
```

### Web Dashboard

```bash
# Start the web dashboard
python3 dashboard.py

# Access at http://localhost:5001
```

## Integration with CI/CD

Add this to your GitHub Actions workflow to include monitoring:

```yaml
- name: Run Monitoring
  env:
    DO_TOKEN: ${{ secrets.DO_TOKEN }}
    APP_URL: ${{ secrets.APP_URL }}
    APP_ID: ${{ secrets.APP_ID }}
  run: |
    cd monitoring
    pip3 install -r requirements.txt
    python3 monitor.py
```

## Customization

### Adding New Metrics

Edit `monitor.py` to add new metrics:

```python
def get_custom_metrics(self):
    """Add your custom metrics here"""
    # Your custom metric collection logic
    pass
```

### Custom Visualizations

Modify the `create_visualizations` method to add new charts:

```python
def create_visualizations(self, metrics_data, health_data):
    # Add your custom chart creation logic
    pass
```

### Alerting

Add custom alerting by extending the monitoring script:

```python
def send_alert(self, message):
    """Send alerts via email, Slack, etc."""
    # Your alerting logic
    pass
```

## Troubleshooting

### Common Issues

1. **API Token Issues**
   - Ensure your `DO_TOKEN` is valid and has read permissions
   - Check that the token hasn't expired

2. **App ID Not Found**
   - Verify your `APP_ID` is correct
   - Ensure the app exists in your DigitalOcean account

3. **Health Check Failures**
   - Check that your app is running and accessible
   - Verify the `/health` endpoint is working

4. **Missing Dependencies**
   - Run `pip3 install -r requirements.txt`
   - Ensure matplotlib is properly installed

### Debug Mode

Run with debug logging:

```bash
export LOG_LEVEL=DEBUG
python3 monitor.py
```

## Security Considerations

- Store API tokens securely (use environment variables)
- Don't commit sensitive data to version control
- Use HTTPS for the web dashboard in production
- Implement authentication for the dashboard if needed

## Performance

The monitoring system is designed to be lightweight:
- Minimal resource usage
- Efficient API calls
- Optimized chart generation
- Automatic cleanup of old data

## Support

For issues or questions:
1. Check the logs in `app_monitor.log`
2. Verify your environment variables
3. Test the DigitalOcean API connectivity
4. Review the troubleshooting section above

## Contributing

To improve the monitoring system:
1. Add new metrics collection methods
2. Enhance visualizations
3. Improve error handling
4. Add new alerting mechanisms
