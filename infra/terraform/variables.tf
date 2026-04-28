variable "artifact_repository_id" {
  description = "Artifact Registry repository ID that stores the Discord service container image."
  type        = string
  default     = "cloud-run-source-deploy"
}

variable "container_port" {
  description = "Container port exposed by the Discord FastAPI service."
  type        = number
  default     = 8080
}

variable "cpu_limit" {
  description = "CPU limit for the Cloud Run container."
  type        = string
  default     = "1000m"
}

variable "discord_redirect_uri" {
  description = "Discord OAuth callback URL for the deployed Cloud Run service."
  type        = string
  default     = "https://discord-service-122083288286.us-east4.run.app/auth/callback"
}

variable "bootstrap_impersonation_member" {
  description = "IAM member allowed to impersonate the CircleCI deployer service account during bootstrap and local imports."
  type        = string
  default     = "user:lh1505@nyu.edu"
}

variable "deployer_service_account_id" {
  description = "Service account ID used by CircleCI to run Terraform deployments."
  type        = string
  default     = "circleci-terraform-deployer"
}

variable "image_uri" {
  description = "Fully qualified Artifact Registry image URI to deploy to Cloud Run."
  type        = string
  default     = "us-east4-docker.pkg.dev/ospsd8-discord/cloud-run-source-deploy/discord-service:67268fef3ab0857ada5a7682d170fcf00c2cf0ce"
}

variable "max_instance_count" {
  description = "Maximum number of Cloud Run instances."
  type        = number
  default     = 20
}

variable "memory_limit" {
  description = "Memory limit for the Cloud Run container."
  type        = string
  default     = "512Mi"
}

variable "min_instance_count" {
  description = "Minimum number of Cloud Run instances."
  type        = number
  default     = 0
}

variable "project_id" {
  description = "Google Cloud project ID for Team 8."
  type        = string
  default     = "ospsd8-discord"
}

variable "region" {
  description = "Google Cloud region for Cloud Run and Artifact Registry."
  type        = string
  default     = "us-east4"
}

variable "runtime_service_account_id" {
  description = "Service account ID for the Cloud Run runtime identity."
  type        = string
  default     = "discord-service-runtime"
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "discord-service"
}
