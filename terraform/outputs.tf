output "production_app_url" {
  value = var.flask_env == "production" ? digitalocean_app.app[0].live_url : null
}

output "testing_app_url" {
  value = var.flask_env == "testing" ? digitalocean_app.testing_app[0].live_url : null
}

# Static ingress IP addresses for Cloudflare A records
output "app_platform_static_ipv4" {
  description = "DigitalOcean App Platform static IPv4 addresses for DNS A records"
  value       = local.app_platform_static_ips.ipv4
}