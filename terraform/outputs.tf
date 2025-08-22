output "app_url" {
  value = length(digitalocean_app.app) > 0 ? digitalocean_app.app[0].live_url : digitalocean_app.testing_app[0].live_url
}