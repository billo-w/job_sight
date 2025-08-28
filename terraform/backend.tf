terraform {
  required_version = ">= 1.6.3"
  backend "s3" {
    endpoints = {
      s3 = "https://lon1.digitaloceanspaces.com"
    }
    bucket                      = "job-sight-terraform"
    # Dynamic key will be set via terraform init -backend-config
    # Production: terraform.tfstate
    # Testing: testing-{branch-name}.tfstate
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_s3_checksum            = true
    skip_requesting_account_id  = true
    region                      = "us-east-1"
  }
}