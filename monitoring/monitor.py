#!/usr/bin/env python3
"""
Job Sight Application Monitoring Script
Uses DigitalOcean API to monitor application infrastructure and create custom visualizations
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

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
        
        # Create directories if they don't exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('charts', exist_ok=True)
    
    def get_app_metrics(self):
        """Get application metrics from DigitalOcean App Platform"""
        try:
            url = f"https://api.digitalocean.com/v2/apps/{self.app_id}/metrics"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            metrics = response.json()
            print(f"Retrieved metrics for app {self.app_id}")
            return metrics
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to get app metrics: {e}")
            return None
    
    def get_app_health(self):
        """Check application health endpoint"""
        try:
            if not self.app_url:
                print("APP_URL not set, skipping health check")
                return None
            
            response = requests.get(f"{self.app_url}/health", timeout=10)
            response.raise_for_status()
            
            health_data = response.json()
            print("Application health check successful")
            return health_data
            
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def create_visualizations(self, metrics_data, health_data):
        """Create custom visualizations of application metrics"""
        if not metrics_data:
            print("No metrics data available for visualization")
            return
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Job Sight Application Monitoring Dashboard', fontsize=16, fontweight='bold')
        
        # 1. CPU Usage Over Time
        if metrics_data.get('cpu_usage'):
            axes[0, 0].plot(metrics_data['cpu_usage'], color='#007bff', linewidth=2)
            axes[0, 0].set_title('CPU Usage (%)', fontweight='bold')
            axes[0, 0].set_ylabel('CPU %')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].set_ylim(0, 100)
        
        # 2. Memory Usage Over Time
        if metrics_data.get('memory_usage'):
            axes[0, 1].plot(metrics_data['memory_usage'], color='#28a745', linewidth=2)
            axes[0, 1].set_title('Memory Usage (%)', fontweight='bold')
            axes[0, 1].set_ylabel('Memory %')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].set_ylim(0, 100)
        
        # 3. Request Count
        if metrics_data.get('request_count'):
            axes[1, 0].bar(range(len(metrics_data['request_count'])), 
                          metrics_data['request_count'], 
                          color='#ffc107', alpha=0.7)
            axes[1, 0].set_title('Request Count', fontweight='bold')
            axes[1, 0].set_ylabel('Requests')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Application Health Status
        if health_data:
            status = health_data.get('status', 'unknown')
            db_status = health_data.get('database', 'unknown')
            env = health_data.get('environment', 'unknown')
            
            # Create a simple status display
            axes[1, 1].text(0.5, 0.7, f'Status: {status.upper()}', 
                           ha='center', va='center', fontsize=14, fontweight='bold',
                           color='green' if status == 'healthy' else 'red')
            axes[1, 1].text(0.5, 0.5, f'Database: {db_status}', 
                           ha='center', va='center', fontsize=12)
            axes[1, 1].text(0.5, 0.3, f'Environment: {env}', 
                           ha='center', va='center', fontsize=12)
            axes[1, 1].set_title('Application Health', fontweight='bold')
            axes[1, 1].axis('off')
        
        # Adjust layout and save
        plt.tight_layout()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chart_path = f'charts/dashboard_{timestamp}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard saved to {chart_path}")
        return chart_path
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        print("Starting monitoring cycle...")
        
        # Get application metrics
        metrics = self.get_app_metrics()
        
        # Get application health
        health = self.get_app_health()
        
        # Create visualizations
        chart_path = self.create_visualizations(metrics, health)
        
        # Print summary
        print("Monitoring cycle completed")
        if health:
            print(f"App Status: {health.get('status', 'unknown')}")
        
        return {
            'metrics': metrics,
            'health': health,
            'chart_path': chart_path
        }

def main():
    """Main function to run monitoring"""
    try:
        monitor = JobSightMonitor()
        
        # Run monitoring cycle
        results = monitor.run_monitoring_cycle()
        
        # Print summary to console
        print("\n" + "="*50)
        print("JOB SIGHT MONITORING SUMMARY")
        print("="*50)
        if results['health']:
            print(f"Application Status: {results['health'].get('status', 'unknown')}")
            print(f"Database Status: {results['health'].get('database', 'unknown')}")
            print(f"Environment: {results['health'].get('environment', 'unknown')}")
        
        if results['chart_path']:
            print(f"\nDashboard saved to: {results['chart_path']}")
        
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
