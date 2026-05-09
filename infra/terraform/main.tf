resource "google_project_service" "required" {
  for_each = local.required_services

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "discord_service" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_repository_id
  description   = "Cloud Run Source Deployments"
  format        = "DOCKER"
  labels        = local.common_labels

  depends_on = [
    google_project_service.required["artifactregistry.googleapis.com"],
  ]
}

resource "google_service_account" "deployer" {
  account_id   = var.deployer_service_account_id
  display_name = "CircleCI Terraform deployer"
  description  = "Deployment identity used by CircleCI to run Terraform for the Discord service."
  project      = var.project_id

  depends_on = [
    google_project_service.required["iam.googleapis.com"],
  ]

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_project_iam_member" "deployer" {
  for_each = local.deployer_project_roles

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_service_account_iam_member" "bootstrap_token_creator" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = var.bootstrap_impersonation_member
}

resource "google_service_account" "runtime" {
  account_id   = var.runtime_service_account_id
  display_name = "Discord Service Cloud Run runtime"
  description  = "Runtime identity for the Team 8 Discord Cloud Run service."
  project      = var.project_id

  depends_on = [
    google_project_service.required["iam.googleapis.com"],
  ]
}

resource "google_secret_manager_secret" "app_secret" {
  for_each = local.app_secret_ids

  project   = var.project_id
  secret_id = each.value
  labels    = local.common_labels

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [
    google_project_service.required["secretmanager.googleapis.com"],
  ]
}

resource "google_secret_manager_secret_iam_member" "runtime_secret_accessor" {
  for_each = local.app_secret_ids

  project   = var.project_id
  secret_id = google_secret_manager_secret.app_secret[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "discord_service" {
  name                = var.service_name
  location            = var.region
  project             = var.project_id
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = true

  scaling {
    min_instance_count = var.min_instance_count
  }

  template {
    service_account                  = google_service_account.runtime.email
    timeout                          = "300s"
    max_instance_request_concurrency = 80

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }

    containers {
      name  = "discord-service-1"
      image = var.image_uri

      ports {
        name           = "http1"
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }

        startup_cpu_boost = true
      }

      env {
        name  = "DISCORD_REDIRECT_URI"
        value = var.discord_redirect_uri
      }

      dynamic "env" {
        for_each = local.app_secret_ids

        content {
          name = env.key

          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.app_secret[env.key].secret_id
              version = "latest"
            }
          }
        }
      }

      dynamic "env" {
        for_each = local.app_mounted_secrets

        content {
          name  = env.value.env_var
          value = "${env.value.mount_path}/${env.value.file_name}"
        }
      }

      dynamic "volume_mounts" {
        for_each = local.app_mounted_secrets

        content {
          name       = volume_mounts.value.secret_id
          mount_path = volume_mounts.value.mount_path
        }
      }

      startup_probe {
        failure_threshold = 1
        period_seconds    = 240
        timeout_seconds   = 240

        tcp_socket {
          port = var.container_port
        }
      }
    }

    dynamic "volumes" {
      for_each = local.app_mounted_secrets

      content {
        name = volumes.value.secret_id

        secret {
          secret = volumes.value.secret_id

          items {
            path    = volumes.value.file_name
            version = "latest"
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_artifact_registry_repository.discord_service,
    google_project_service.required["run.googleapis.com"],
    google_secret_manager_secret_iam_member.runtime_secret_accessor,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.discord_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
