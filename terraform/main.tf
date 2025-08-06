terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token       = var.do_token
}

resource "digitalocean_container_registry" "app_registry" {
  name                   = "job-sight-app"
  subscription_tier_slug = "basic"
}

resource "digitalocean_project" "project" {
  name        = "Job-Sight-Project"
  resources   = [
    digitalocean_app.app.urn,
    digitalocean_container_registry.app_registry.urn
  ]
}

resource "digitalocean_app" "app" {
  spec {
    name = "job-sight-app"
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
        repository    = "job-sight-app/job-sight"
        tag           = "latest"
        deploy_on_push {
          enabled = true
        }
      }
      log_destination {
        name = "logtail"
        logtail {
          token = var.logtail_source_token
        }
      }
      alert {
        rule = "CPU_UTILIZATION"
        value = 70
        operator = "GREATER_THAN"
        window = "FIVE_MINUTES"
        disabled = false
      }
      alert {
        rule = "MEM_UTILIZATION"
        value = 70
        operator = "GREATER_THAN"
        window = "FIVE_MINUTES"
        disabled = false
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
      env {
        key   = "LOGTAIL_SOURCE_TOKEN"
        value = var.logtail_source_token
      }
    }
  }
}