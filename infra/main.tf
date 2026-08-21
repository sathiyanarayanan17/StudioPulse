# Google Cloud Infrastructure for StudioPulse AI
# Terraform configuration

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
  }
}

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "monitoring.googleapis.com",
    "container.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# GKE Cluster for Render Pipeline (simulated workload)
resource "google_container_cluster" "render_cluster" {
  name     = "render-cluster"
  location = var.region

  initial_node_count       = 1
  remove_default_node_pool = true

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  depends_on = [google_project_service.apis]
}

# GPU Node Pool for rendering
resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  location   = var.region
  cluster    = google_container_cluster.render_cluster.name
  node_count = 3

  autoscaling {
    min_node_count = 1
    max_node_count = 10
  }

  node_config {
    machine_type = "n1-standard-8"

    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      role = "render-worker"
    }
  }
}

# Service Account for StudioPulse AI
resource "google_service_account" "studiopulse" {
  account_id   = "studiopulse-ai"
  display_name = "StudioPulse AI Agent"
}

# IAM bindings
resource "google_project_iam_member" "studiopulse_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/monitoring.viewer",
    "roles/container.developer",
    "roles/compute.instanceAdmin.v1",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.studiopulse.email}"
}

# Cloud Run for StudioPulse AI agent
resource "google_cloud_run_v2_service" "studiopulse" {
  name     = "studiopulse-ai"
  location = var.region

  template {
    service_account = google_service_account.studiopulse.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/studiopulse/agent:latest"

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_REGION"
        value = var.region
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Outputs
output "cluster_endpoint" {
  value = google_container_cluster.render_cluster.endpoint
}

output "service_url" {
  value = google_cloud_run_v2_service.studiopulse.uri
}

output "service_account_email" {
  value = google_service_account.studiopulse.email
}
