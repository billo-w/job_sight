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

variable "logtail_source_token" {
  description = "Logtail source token for logging"
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