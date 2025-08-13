terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.45.0"
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

resource "digitalocean_app" "app" {
  # Ensure registry is created first
  depends_on = [digitalocean_container_registry.app_registry]

  project_id = var.project_id

  spec {
    name   = "job-sight-app"
    region = "lon"

    alert {
      rule = "DEPLOYMENT_FAILED"
      destinations {
          emails = [var.email]
          slack_webhooks {
            channel = var.slack_channel
            url     = var.slack_webhook_url
          }
        }
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

      log_destination {
        name = "do_logtaiil"
        logtail {
          token = var.logtail_token
        }
      }

      alert {
        rule     = "CPU_UTILIZATION"
        value    = 70
        operator = "GREATER_THAN"
        window   = "FIVE_MINUTES"
        disabled = false

        destinations {
          emails = [var.email]
          slack_webhooks {
            channel = var.slack_channel
            url     = var.slack_webhook_url
          }
        }

      }
      alert {
        rule     = "MEM_UTILIZATION"
        value    = 70
        operator = "GREATER_THAN"
        window   = "FIVE_MINUTES"
        disabled = false

        destinations {
          emails = [var.email]
          slack_webhooks {
            channel = var.slack_channel
            url     = var.slack_webhook_url
          }
        }        
      }
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
    }
  }

  timeouts {
    create = "20m"
  }
}
