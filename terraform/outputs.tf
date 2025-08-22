output "app_url" {
  value = var.flask_env == "production" ? digitalocean_app.app[0].live_url : digitalocean_app.testing_app[0].live_url
}