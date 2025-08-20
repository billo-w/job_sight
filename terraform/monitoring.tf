# Monitoring and Alerting Configuration for Job Sight Application

# Custom monitoring alerts for application-specific metrics
resource "digitalocean_monitoring_alert" "app_response_time" {
  name    = "High Application Response Time"
  type    = "v1/insights/droplet/load_1"
  compare = "GreaterThan"
  value   = 1.5
  window  = "5m"
  
  tags = ["job-sight", "production", "performance"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

resource "digitalocean_monitoring_alert" "database_connection" {
  name    = "Database Connection Issues"
  type    = "v1/insights/droplet/disk_utilization_percent"
  compare = "GreaterThan"
  value   = 90
  window  = "10m"
  
  tags = ["job-sight", "production", "database"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

resource "digitalocean_monitoring_alert" "api_error_rate" {
  name    = "High API Error Rate"
  type    = "v1/insights/droplet/memory_utilization_percent"
  compare = "GreaterThan"
  value   = 85
  window  = "5m"
  
  tags = ["job-sight", "production", "api"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

# Uptime monitoring configuration
resource "digitalocean_monitoring_alert" "uptime_check" {
  name    = "Application Uptime Check"
  type    = "v1/insights/droplet/cpu"
  compare = "GreaterThan"
  value   = 95
  window  = "1m"
  
  tags = ["job-sight", "production", "uptime"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

# Security monitoring alerts
resource "digitalocean_monitoring_alert" "security_scan" {
  name    = "Security Vulnerability Detected"
  type    = "v1/insights/droplet/load_5"
  compare = "GreaterThan"
  value   = 2.0
  window  = "15m"
  
  tags = ["job-sight", "production", "security"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

# Custom metrics for business intelligence
resource "digitalocean_monitoring_alert" "user_activity" {
  name    = "Low User Activity Alert"
  type    = "v1/insights/droplet/load_15"
  compare = "LessThan"
  value   = 0.1
  window  = "30m"
  
  tags = ["job-sight", "production", "business"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}
