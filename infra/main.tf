# OpenTofu
# Configure the OpenTofu provider for OVHcloud (placeholder)
terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 0.35"
    }
  }
}

provider "ovh" {
  endpoint           = "ovh-eu"
  application_key    = "YOUR_APP_KEY"
  application_secret = "YOUR_APP_SECRET"
  consumer_key       = "YOUR_CONSUMER_KEY"
}

# Define a sovereign S3 Bucket in Gravelines (GRA)
resource "ovh_cloud_project_s3_bucket" "model_storage" {
  project_id = "YOUR_PUBLIC_CLOUD_PROJECT_ID"
  name       = "agentic-architect-models"
  region     = "GRA" # Data remains in France
}

# Output the bucket URL to use in your scripts
output "s3_bucket_url" {
  value = "https://${ovh_cloud_project_s3_bucket.model_storage.name}.s3.gra.perf.cloud.ovh.net"
}