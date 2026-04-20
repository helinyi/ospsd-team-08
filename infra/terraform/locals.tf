locals {
  app_secret_ids = {
    DISCORD_BOT_TOKEN     = "discord-bot-token"
    DISCORD_CLIENT_ID     = "discord-client-id"
    DISCORD_CLIENT_SECRET = "discord-client-secret"
    DISCORD_GUILD_ID      = "discord-guild-id"
    SESSION_SECRET_KEY    = "session-secret-key"
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
