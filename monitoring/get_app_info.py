#!/usr/bin/env python3
"""
Helper script to get DigitalOcean App information
This script helps you find your App ID and other useful information
"""

import os
import requests
import json

def get_apps_info():
    """Get information about all your DigitalOcean apps"""
    do_token = os.environ.get('DO_TOKEN')
    
    if not do_token:
        print("❌ Error: DO_TOKEN environment variable is required")
        print("Please set your DigitalOcean API token:")
        print("export DO_TOKEN=your_token_here")
        return
    
    headers = {
        'Authorization': f'Bearer {do_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get all apps
        url = "https://api.digitalocean.com/v2/apps"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        apps_data = response.json()
        apps = apps_data.get('apps', [])
        
        if not apps:
            print("📭 No apps found in your DigitalOcean account")
            return
        
        print("🔍 Found the following apps in your DigitalOcean account:")
        print("=" * 80)
        
        for app in apps:
            print(f"📱 App Name: {app.get('spec', {}).get('name', 'Unknown')}")
            print(f"🆔 App ID: {app.get('id', 'Unknown')}")
            print(f"🌍 Region: {app.get('spec', {}).get('region', 'Unknown')}")
            print(f"📊 Status: {app.get('live_url', 'Not deployed')}")
            print(f"🕒 Created: {app.get('created_at', 'Unknown')}")
            print("-" * 80)
        
        # Look for Job Sight app specifically
        job_sight_apps = [app for app in apps if 'job' in app.get('spec', {}).get('name', '').lower() or 'sight' in app.get('spec', {}).get('name', '').lower()]
        
        if job_sight_apps:
            print("\n🎯 Job Sight related apps found:")
            for app in job_sight_apps:
                print(f"✅ {app.get('spec', {}).get('name')} - ID: {app.get('id')}")
                print(f"   URL: {app.get('live_url', 'Not deployed')}")
        else:
            print("\n⚠️  No apps with 'job' or 'sight' in the name found")
            print("   You can use any of the app IDs above for monitoring")
        
        print("\n📋 To use with monitoring, set these environment variables:")
        print(f"export APP_ID=\"{apps[0].get('id')}\"  # Use the appropriate app ID")
        print(f"export APP_URL=\"{apps[0].get('live_url', 'your-app-url')}\"  # Use your app URL")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching app information: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def get_app_details(app_id):
    """Get detailed information about a specific app"""
    do_token = os.environ.get('DO_TOKEN')
    
    if not do_token:
        print("❌ Error: DO_TOKEN environment variable is required")
        return
    
    headers = {
        'Authorization': f'Bearer {do_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"https://api.digitalocean.com/v2/apps/{app_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        app_data = response.json()
        app = app_data.get('app', {})
        
        print(f"📱 Detailed information for app: {app.get('spec', {}).get('name', 'Unknown')}")
        print("=" * 80)
        print(f"🆔 App ID: {app.get('id')}")
        print(f"🌍 Region: {app.get('spec', {}).get('region')}")
        print(f"📊 Live URL: {app.get('live_url', 'Not deployed')}")
        print(f"🕒 Created: {app.get('created_at')}")
        print(f"📝 Updated: {app.get('updated_at')}")
        
        # Services information
        services = app.get('spec', {}).get('services', [])
        print(f"\n🔧 Services ({len(services)}):")
        for service in services:
            print(f"  - {service.get('name')}: {service.get('instance_count')} instances")
            print(f"    Size: {service.get('instance_size_slug')}")
            print(f"    Port: {service.get('http_port')}")
        
        # Environment variables
        env_vars = []
        for service in services:
            env_vars.extend(service.get('env', []))
        
        if env_vars:
            print(f"\n🔑 Environment Variables ({len(env_vars)}):")
            for env_var in env_vars:
                key = env_var.get('key', 'Unknown')
                value = env_var.get('value', 'Not set')
                # Mask sensitive values
                if any(sensitive in key.lower() for sensitive in ['key', 'token', 'secret', 'password']):
                    value = '*' * len(value) if value else 'Not set'
                print(f"  - {key}: {value}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching app details: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        app_id = sys.argv[1]
        get_app_details(app_id)
    else:
        get_apps_info()

if __name__ == "__main__":
    main()
