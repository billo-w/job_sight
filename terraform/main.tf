terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.40.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_container_registry" "app_registry" {
  name                   = "job-sight-app"
  subscription_tier_slug = "basic"
}

resource "digitalocean_project" "project" {
  name        = "Job-Sight-Project"
  description = "Job Sight Application Project"
  purpose     = "Web Application"
  environment = "Production"
  is_default  = true
  # Remove the direct dependency to avoid circular reference issues
  # Resources can be added after app creation
}

resource "digitalocean_app" "app" {
  # Ensure registry is created first
  depends_on = [digitalocean_container_registry.app_registry]

  spec {
    name   = "job-sight-app"
    region = "lon"

    alert {
      rule = "DEPLOYMENT_FAILED"
    }

    service {
      name               = "job-sight"
      instance_count     = 1
      instance_size_slug = "apps-s-1vcpu-0.5gb"
      http_port          = 8080

      image {
        registry_type = "DOCR"
        repository    = "job-sight"
        tag           = "latest"
        deploy_on_push {
          enabled = true
        }
      }

      # Enhanced logging configuration
      log_destination {
        name = "do_logtail"
        logtail {
          token = var.logtail_token
        }
      }

      # Health check configuration
      health_check {
        http_path = "/health"
        initial_delay_seconds = 30
        period_seconds = 60
        timeout_seconds = 10
        success_threshold = 1
        failure_threshold = 3
      }

      # Service-level alerts
      alert {
        rule     = "CPU_UTILIZATION"
        value    = 70
        operator = "GREATER_THAN"
        window   = "FIVE_MINUTES"
        disabled = false
      }
      
      alert {
        rule     = "MEM_UTILIZATION"
        value    = 80
        operator = "GREATER_THAN"
        window   = "FIVE_MINUTES"
        disabled = false
      }

      # Environment variables for monitoring
      env {
        key   = "SECRET_KEY"
        value = var.secret_key
      }
      env {
        key   = "FLASK_ENV"
        value = var.flask_env
      }
      env {
        key   = "DATABASE_URL"
        value = var.database_url
      }
      env {
        key   = "ADZUNA_APP_ID"
        value = var.adzuna_app_id
      }
      env {
        key   = "ADZUNA_APP_KEY"
        value = var.adzuna_app_key
      }
      env {
        key   = "AZURE_AI_ENDPOINT"
        value = var.azure_ai_endpoint
      }
      env {
        key   = "AZURE_AI_KEY"
        value = var.azure_ai_key
      }
      # Monitoring environment variables
      env {
        key   = "APP_VERSION"
        value = "1.0.0"
      }
      env {
        key   = "ENABLE_METRICS"
        value = "true"
      }
      env {
        key   = "LOG_LEVEL"
        value = "INFO"
      }
    }
  }

  timeouts {
    create = "20m"
  }
}

# Add project resources after app creation to avoid dependency issues
resource "digitalocean_project_resources" "project_resources" {
  project = digitalocean_project.project.id
  resources = [
    digitalocean_app.app.urn
  ]
  
  depends_on = [
    digitalocean_app.app
  ]
}

# Monitoring dashboard configuration
resource "digitalocean_monitoring_alert" "high_cpu" {
  name    = "High CPU Usage Alert"
  type    = "v1/insights/droplet/cpu"
  compare = "GreaterThan"
  value   = 80
  window  = "5m"
  
  tags = ["job-sight", "production"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

resource "digitalocean_monitoring_alert" "high_memory" {
  name    = "High Memory Usage Alert"
  type    = "v1/insights/droplet/memory_utilization_percent"
  compare = "GreaterThan"
  value   = 85
  window  = "5m"
  
  tags = ["job-sight", "production"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}

resource "digitalocean_monitoring_alert" "app_health" {
  name    = "Application Health Check Alert"
  type    = "v1/insights/droplet/load_1"
  compare = "GreaterThan"
  value   = 2.0
  window  = "10m"
  
  tags = ["job-sight", "production"]
  
  notification {
    email = [var.email]
    slack {
      channel = var.slack_channel
      url     = var.slack_webhook_url
    }
  }
}
