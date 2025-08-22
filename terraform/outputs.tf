output "production_app_url" {
  value = var.flask_env == "production" ? digitalocean_app.app[0].live_url : null
}

output "testing_app_url" {
  value = var.flask_env == "testing" ? digitalocean_app.testing_app[0].live_url : null
}