#!/usr/bin/env python3
"""
Job Sight Live Monitoring Dashboard
Single script that provides a live web dashboard for monitoring
"""

from flask import Flask, render_template_string, jsonify
import requests
import os
from datetime import datetime
import json

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Sight Live Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header { 
            background: rgba(255,255,255,0.95); 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { color: #2d3748; margin-bottom: 10px; }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }
        .card { 
            background: rgba(255,255,255,0.95); 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h3 { color: #2d3748; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        .status-item { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 10px; 
            padding: 8px 0; 
        }
        .status-value { 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-weight: bold; 
        }
        .healthy { background: #c6f6d5; color: #22543d; }
        .error { background: #fed7d7; color: #742a2a; }
        .warning { background: #fef5e7; color: #744210; }
        .unknown { background: #e2e8f0; color: #4a5568; }
        .refresh-btn { 
            background: #4299e1; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px 5px;
        }
        .refresh-btn:hover { background: #3182ce; }
        .timestamp { 
            text-align: center; 
            color: #718096; 
            font-size: 0.9rem; 
            margin-top: 20px; 
        }
        .loading { text-align: center; padding: 20px; color: #718096; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Job Sight Live Dashboard</h1>
            <p>Real-time application and infrastructure monitoring</p>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
            <button class="refresh-btn" onclick="location.reload()">📊 Reload</button>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📱 Application Status</h3>
                <div id="app-status">
                    <div class="loading">Loading...</div>
                </div>
            </div>

            <div class="card">
                <h3>⚡ Performance Metrics</h3>
                <div id="metrics">
                    <div class="loading">Loading...</div>
                </div>
            </div>

            <div class="card">
                <h3>🔧 System Info</h3>
                <div id="system-info">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>

        <div class="timestamp" id="timestamp">
            Last updated: Loading...
        </div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update app status
                    const appStatus = document.getElementById('app-status');
                    if (data.health) {
                        const status = data.health.status || 'unknown';
                        const dbStatus = data.health.database || 'unknown';
                        const env = data.health.environment || 'unknown';
                        
                        appStatus.innerHTML = `
                            <div class="status-item">
                                <span>Overall Health:</span>
                                <span class="status-value ${status === 'healthy' ? 'healthy' : 'error'}">${status}</span>
                            </div>
                            <div class="status-item">
                                <span>Database:</span>
                                <span class="status-value ${dbStatus.includes('connected') ? 'healthy' : 'error'}">${dbStatus}</span>
                            </div>
                            <div class="status-item">
                                <span>Environment:</span>
                                <span class="status-value unknown">${env}</span>
                            </div>
                        `;
                    } else {
                        appStatus.innerHTML = '<div class="status-item"><span>Status:</span><span class="status-value error">Unavailable</span></div>';
                    }

                    // Update metrics
                    const metrics = document.getElementById('metrics');
                    if (data.metrics && data.metrics.metrics) {
                        let metricsHtml = '';
                        data.metrics.metrics.forEach(metric => {
                            const name = metric.name || 'Unknown';
                            const value = metric.values ? metric.values[metric.values.length - 1] : 'N/A';
                            const avgValue = metric.values ? (metric.values.reduce((a, b) => a + b, 0) / metric.values.length).toFixed(2) : 'N/A';
                            
                            metricsHtml += `
                                <div class="status-item">
                                    <span>${name}:</span>
                                    <span class="status-value ${value > 80 ? 'warning' : 'healthy'}">${value}</span>
                                </div>
                                <div class="status-item">
                                    <span>${name} (Avg):</span>
                                    <span class="status-value ${avgValue > 80 ? 'warning' : 'healthy'}">${avgValue}</span>
                                </div>
                            `;
                        });
                        metrics.innerHTML = metricsHtml || '<div class="status-item"><span>No metrics available</span></div>';
                    } else {
                        metrics.innerHTML = '<div class="status-item"><span>No metrics available</span></div>';
                    }

                    // Update system info
                    const systemInfo = document.getElementById('system-info');
                    systemInfo.innerHTML = `
                        <div class="status-item">
                            <span>Last Updated:</span>
                            <span class="status-value unknown">${new Date().toLocaleString()}</span>
                        </div>
                        <div class="status-item">
                            <span>Monitoring Status:</span>
                            <span class="status-value healthy">Active</span>
                        </div>
                        <div class="status-item">
                            <span>Data Source:</span>
                            <span class="status-value unknown">DigitalOcean API</span>
                        </div>
                    `;

                    // Update timestamp
                    document.getElementById('timestamp').textContent = `Last updated: ${new Date().toLocaleString()}`;
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('app-status').innerHTML = '<div class="status-item"><span>Error:</span><span class="status-value error">Failed to load</span></div>';
                    document.getElementById('metrics').innerHTML = '<div class="status-item"><span>Error:</span><span class="status-value error">Failed to load</span></div>';
                    document.getElementById('system-info').innerHTML = '<div class="status-item"><span>Error:</span><span class="status-value error">Failed to load</span></div>';
                });
        }

        function refreshData() {
            updateDashboard();
        }

        // Update every 30 seconds
        updateDashboard();
        setInterval(updateDashboard, 30000);
    </script>
</body>
</html>
"""

class JobSightMonitor:
    def __init__(self):
        self.do_token = os.environ.get('DO_TOKEN')
        self.app_url = os.environ.get('APP_URL')
        self.app_id = os.environ.get('APP_ID')
        
        if not self.do_token:
            raise ValueError("DO_TOKEN environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.do_token}',
            'Content-Type': 'application/json'
        }
    
    def get_app_metrics(self):
        """Get application metrics from DigitalOcean App Platform"""
        try:
            if not self.app_id:
                return None
                
            url = f"https://api.digitalocean.com/v2/apps/{self.app_id}/metrics"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to get app metrics: {e}")
            return None
    
    def get_app_health(self):
        """Check application health endpoint"""
        try:
            if not self.app_url:
                return None
            
            response = requests.get(f"{self.app_url}/health", timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None

# Create monitor instance
monitor = JobSightMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    try:
        health = monitor.get_app_health()
        metrics = monitor.get_app_metrics()
        
        return jsonify({
            'status': 'success',
            'health': health,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🚀 Starting Job Sight Live Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔄 Data refreshes automatically every 30 seconds")
    print("=" * 50)
    
    app.run(debug=False, host='127.0.0.1', port=5001)
