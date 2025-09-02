terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.40.0"
    }
  }
}

# Separate app for testing environments
resource "digitalocean_app" "testing_app" {
  # Only create this resource if it's a testing environment
  count = var.flask_env == "testing" ? 1 : 0

  spec {
    name   = var.app_name
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
        tag           = var.image_tag
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
        type = "SECRET"
      }
      env {
        key   = "FLASK_ENV"
        value = var.flask_env
        type = "SECRET"
      }
      env {
        key   = "DATABASE_URL"
        value = var.database_url
        type = "SECRET"
      }
      env {
        key   = "ADZUNA_APP_ID"
        value = var.adzuna_app_id
        type = "SECRET"
      }
      env {
        key   = "ADZUNA_APP_KEY"
        value = var.adzuna_app_key
        type = "SECRET"
      }
      env {
        key   = "AZURE_AI_ENDPOINT"
        value = var.azure_ai_endpoint
        type = "SECRET"
      }
      env {
        key   = "AZURE_AI_KEY"
        value = var.azure_ai_key
        type = "SECRET"
      }
      # Monitoring environment variables
      env {
        key   = "APP_VERSION"
        value = var.app_version
        type = "SECRET"
      }
      env {
        key   = "ENABLE_METRICS"
        value = "true"
        type = "SECRET"
      }
      env {
        key   = "LOG_LEVEL"
        value = "INFO"
        type = "SECRET"
      }
      # IP restriction environment variables
      env {
        key   = "ENABLE_IP_RESTRICTIONS"
        value = var.enable_ip_restrictions ? "true" : "false"
        type = "SECRET"
      }
      env {
        key   = "ALLOWED_IPS"
        value = join(",", var.allowed_ips)
        type = "SECRET"
      }
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Only create registry and project in production environment
# Testing environments will use the existing ones
resource "digitalocean_container_registry" "app_registry" {
  count                  = var.flask_env == "production" ? 1 : 0
  name                   = "job-sight-app"
  subscription_tier_slug = "basic"
}

resource "digitalocean_project" "project" {
  count       = var.flask_env == "production" ? 1 : 0
  name        = "Job-Sight-Project"
  description = "Job Sight Application Project"
  purpose     = "Web Application"
  environment = "Production"
  is_default  = true
}

resource "digitalocean_app" "app" {
  # Ensure registry is created first (only in production)
  depends_on = [digitalocean_container_registry.app_registry]
  
  # Only create this resource if it's not a testing environment
  count = var.flask_env == "production" ? 1 : 0

  spec {
    name   = var.app_name
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
        tag           = var.image_tag
        deploy_on_push {
          enabled = var.flask_env == "testing"
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
        value = var.app_version
      }
      env {
        key   = "ENABLE_METRICS"
        value = "true"
      }
      env {
        key   = "LOG_LEVEL"
        value = "INFO"
      }
      # IP restriction environment variables
      env {
        key   = "ENABLE_IP_RESTRICTIONS"
        value = var.enable_ip_restrictions ? "true" : "false"
      }
      env {
        key   = "ALLOWED_IPS"
        value = join(",", var.allowed_ips)
      }
    }
    env {
      key   = "ALLOWED_IPS"
      value = join(",", var.allowed_ips)
    }
  }

  timeouts {
    create = "20m"
  }
}

# Project resources assignment removed to avoid conflicts
# Apps will be manually added to the project if needed

# Note: DigitalOcean App Platform has built-in monitoring and alerting
# The monitoring configuration is handled through the app spec alerts
# Custom monitoring alerts can be configured through the DigitalOcean dashboard

# Additional monitoring configuration
# The monitoring system is now available in the monitoring/ directory
# It provides custom visualizations and enhanced monitoring capabilities
# using DigitalOcean's API to create custom dashboards and reports
