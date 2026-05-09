locals {
  app_secret_ids = {
    DISCORD_BOT_TOKEN     = "discord-bot-token"
    DISCORD_CLIENT_ID     = "discord-client-id"
    DISCORD_CLIENT_SECRET = "discord-client-secret"
    DISCORD_GUILD_ID      = "discord-guild-id"
    SESSION_SECRET_KEY    = "session-secret-key"
  }

  # Secret Manager secrets that are mounted into the container as files
  # (rather than injected as env vars). The secret resources themselves are
  # created out-of-band via gcloud; Terraform only owns the Cloud Run mount
  # and the env var that points to the mounted file path.
  app_mounted_secrets = {
    credentials = {
      secret_id  = "google-oauth-credentials"
      mount_path = "/secrets/oauth-credentials"
      file_name  = "credentials.json"
      env_var    = "GOOGLE_OAUTH_CREDENTIALS_PATH"
    }
    token = {
      secret_id  = "google-oauth-token"
      mount_path = "/secrets/oauth-token"
      file_name  = "token.json"
      env_var    = "GOOGLE_OAUTH_TOKEN_PATH"
    }
  }

  common_labels = {
    app        = var.service_name
    component  = "discord-service"
    managed_by = "terraform"
  }

  deployer_project_roles = toset([
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.editor",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/resourcemanager.projectIamAdmin",
    "roles/run.admin",
    "roles/secretmanager.admin",
    "roles/serviceusage.serviceUsageAdmin",
    "roles/storage.admin",
    "roles/viewer",
  ])

  required_services = toset([
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
  ])
}
