variable "do_token" {
  description = "DigitalOcean API token for App Platform & Spaces"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repo in format user/repo"
  type        = string
}

variable "adzuna_app_id" {
  description = "Adzuna API Application ID"
  type        = string
  sensitive   = true
}

variable "adzuna_app_key" {
  description = "Adzuna API Key"
  type        = string
  sensitive   = true
}

variable "azure_ai_endpoint" {
  description = "Azure AI service endpoint URL"
  type        = string
}

variable "azure_ai_key" {
  description = "Azure AI API key"
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Connection string for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask secret key for session management"
  type        = string
  sensitive   = true
}

variable "flask_env" {
  description = "Flask environment (development, production, etc.)"
  type        = string
  default     = "production"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  sensitive   = true
}

variable "slack_channel" {
  description = "Slack channel for alerts"
  type        = string
  default     = "#alert-tracker"
}

variable "email" {
  description = "Email address for alert notifications"
  type        = string
}

variable "logtail_token" {
  description = "Logtail token for log management"
  type        = string
  sensitive   = true
}

variable "project_id" {
  description = "DigitalOcean project ID for the application"
  type        = string
}

variable "allowed_ips" {
  description = "List of IP addresses allowed to access the application (CIDR notation)"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Allow all IPs by default
}

variable "enable_ip_restrictions" {
  description = "Enable IP restrictions for the application"
  type        = bool
  default     = false
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "job-sight-app"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "app_version" {
  description = "Application version"
  type        = string
  default     = "1.0.0"
}