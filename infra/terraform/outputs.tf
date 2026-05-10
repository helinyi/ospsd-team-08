output "artifact_repository_url" {
  description = "Artifact Registry Docker repository URL."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.discord_service.repository_id}"
}

output "deployer_service_account_email" {
  description = "CircleCI Terraform deployer service account email."
  value       = google_service_account.deployer.email
}

output "managed_secret_ids" {
  description = "Secret Manager secret IDs managed by Terraform."
  value       = values(google_secret_manager_secret.app_secret)[*].secret_id
}

output "runtime_service_account_email" {
  description = "Cloud Run runtime service account email."
  value       = google_service_account.runtime.email
}

output "service_name" {
  description = "Cloud Run service name."
  value       = google_cloud_run_v2_service.discord_service.name
}

output "service_url" {
  description = "Cloud Run service URL."
  value       = google_cloud_run_v2_service.discord_service.uri
}
