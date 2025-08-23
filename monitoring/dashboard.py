#!/usr/bin/env python3
"""
Job Sight Monitoring Dashboard
Simple web interface to display application monitoring data
"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
from datetime import datetime
import glob
from monitor import JobSightMonitor

app = Flask(__name__)

# Ensure monitoring directories exist
os.makedirs('monitoring/data', exist_ok=True)
os.makedirs('monitoring/charts', exist_ok=True)
os.makedirs('monitoring/templates', exist_ok=True)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get latest monitoring data
        monitor = JobSightMonitor()
        results = monitor.run_monitoring_cycle()
        
        # Get latest chart
        charts = glob.glob('monitoring/charts/*.png')
        latest_chart = max(charts, key=os.path.getctime) if charts else None
        
        # Get latest report
        reports = glob.glob('monitoring/data/*.json')
        latest_report = max(reports, key=os.path.getctime) if reports else None
        
        if latest_report:
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
        else:
            report_data = {}
        
        return render_template('dashboard.html', 
                             report=report_data,
                             chart_file=os.path.basename(latest_chart) if latest_chart else None,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    except Exception as e:
        return render_template('dashboard.html', 
                             error=str(e),
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    try:
        monitor = JobSightMonitor()
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

@app.route('/charts/<filename>')
def serve_chart(filename):
    """Serve chart images"""
    return send_from_directory('monitoring/charts', filename)

@app.route('/api/refresh')
def refresh_data():
    """Manually refresh monitoring data"""
    try:
        monitor = JobSightMonitor()
        results = monitor.run_monitoring_cycle()
        
        return jsonify({
            'status': 'success',
            'message': 'Monitoring data refreshed successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
