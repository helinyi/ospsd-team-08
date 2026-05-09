# Google Cloud Run Deployment

**Project:** `ospsd8-discord`
**Region:** `us-east4`
**Service URL:** `https://discord-service-122083288286.us-east4.run.app`

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- Authenticated with `gcloud auth login`

## Setup Commands

The original deployment was created manually with `gcloud` and Cloud Build. The current deployment is managed by Terraform in `infra/terraform` and applied by CircleCI.

### 1. Set Active Project

```bash
gcloud config set project ospsd8-discord
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project=ospsd8-discord
```

### 3. Grant IAM Roles to Default Compute Service Account

```bash
PROJECT_NUMBER=122083288286
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:${SA}" \
  --role="roles/cloudbuild.builds.builder" --quiet

gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:${SA}" \
  --role="roles/storage.objectViewer" --quiet

gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:${SA}" \
  --role="roles/artifactregistry.writer" --quiet

gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:${SA}" \
  --role="roles/run.admin" --quiet

gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:${SA}" \
  --role="roles/iam.serviceAccountUser" --quiet
```

### 4. Grant Secret Manager Access to Cloud Build Service Account

```bash
gcloud projects add-iam-policy-binding ospsd8-discord \
  --member="serviceAccount:service-122083288286@gcp-sa-cloudbuild.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin" --quiet
```

### 5. Connect GitHub Repository

```bash
# Create GitHub connection (opens browser for OAuth authorization)
gcloud builds connections create github ospsd-github \
  --region=us-east4 \
  --project=ospsd8-discord

# Link the repository
gcloud builds repositories create ospsd-team-08 \
  --connection=ospsd-github \
  --remote-uri=https://github.com/helinyi/ospsd-team-08.git \
  --region=us-east4 \
  --project=ospsd8-discord
```

### 6. Legacy Cloud Build Trigger

This was the old deployment path. The current pipeline uses CircleCI plus Terraform instead, so this trigger is kept here only as historical context.

```bash
gcloud builds triggers create github \
  --name="deploy-hw2" \
  --repository="projects/ospsd8-discord/locations/us-east4/connections/ospsd-github/repositories/ospsd-team-08" \
  --branch-pattern="^hw-2$" \
  --build-config="cloudbuild.yaml" \
  --region=us-east4 \
  --project=ospsd8-discord \
  --service-account="projects/ospsd8-discord/serviceAccounts/122083288286-compute@developer.gserviceaccount.com"
```

## Terraform Deployment

Terraform code lives in:

```bash
infra/terraform
```

It manages:

- Existing Cloud Run service: `discord-service`
- Existing Artifact Registry repository: `cloud-run-source-deploy`
- Required Google APIs
- CircleCI Terraform deployer service account and IAM
- Cloud Run runtime service account
- Secret Manager secret containers
- IAM for Cloud Run to read secrets
- Public Cloud Run invoker access

### Imported Existing Resources

The existing Google Cloud resources have already been imported into the shared Terraform state at:

```bash
gs://ospsd8-discord-terraform-state/team-08/discord-service/default.tfstate
```

Normal Terraform runs should use the shared backend and do not need import blocks:

```bash
gcloud config set account lh1505@nyu.edu
gcloud config set project ospsd8-discord

terraform -chdir=infra/terraform init \
  -backend-config="bucket=ospsd8-discord-terraform-state" \
  -backend-config="prefix=team-08/discord-service"

terraform -chdir=infra/terraform plan
```

The import covered the existing Cloud Run service, Artifact Registry repository, public invoker IAM binding, required Google APIs, CircleCI deployer service account, deployer IAM bindings, runtime service account, Secret Manager secret containers, and Cloud Run secret-access IAM.

The Cloud Run service previously had Discord credentials configured as plain environment values. Those values have been moved into Secret Manager. Do not copy secret values into Terraform files.

### Re-bootstrapping

The deployment uses a service account impersonation pattern (`bootstrap_impersonation_member`) to avoid committing long-lived keys to CI. This grants a human identity the ability to impersonate the Terraform deployer service account (`circleci-terraform-deployer@ospsd8-discord.iam.gserviceaccount.com`) without storing a key file in source control.

To re-bootstrap from scratch:
1. Authenticate as a project owner: `gcloud auth login`
2. Set the project: `gcloud config set project ospsd8-discord`
3. Initialize Terraform with the remote backend:
```bash
terraform -chdir=infra/terraform init \
  -backend-config="bucket=ospsd8-discord-terraform-state" \
  -backend-config="prefix=team-08/discord-service"
```
4. Run `terraform apply` — this recreates the deployer SA, IAM bindings, and Secret Manager containers
5. Generate a new key for CircleCI (see key rotation instructions above)
6. Store the base64-encoded key in CircleCI as `GCLOUD_SERVICE_KEY`

### CircleCI Variables

Because this repo deploys through CircleCI, use **CircleCI project environment variables** or a **CircleCI context**. GitHub Actions also has repository secrets, but those only apply if the project uses GitHub Actions workflows.

The deployer service account already exists and is managed by Terraform:

```bash
circleci-terraform-deployer@ospsd8-discord.iam.gserviceaccount.com
```

If the key must be rotated, create a new key and store it in CircleCI as `GCLOUD_SERVICE_KEY`:

```bash
CIRCLECI_SA="circleci-terraform-deployer@ospsd8-discord.iam.gserviceaccount.com"

gcloud iam service-accounts keys create circleci-terraform-key.json \
  --iam-account="${CIRCLECI_SA}" \
  --project=ospsd8-discord

base64 -i circleci-terraform-key.json
rm circleci-terraform-key.json
```

Copy the base64 output into the CircleCI variable `GCLOUD_SERVICE_KEY`.

Set these deployment variables in CircleCI:

| Variable | Purpose |
|---|---|
| `GCLOUD_SERVICE_KEY` | Google service account key JSON, either raw JSON or base64-encoded JSON |
| `GOOGLE_PROJECT_ID` | `ospsd8-discord` |
| `GOOGLE_REGION` | `us-east4` |
| `TF_STATE_BUCKET` | `ospsd8-discord-terraform-state` |
| `TF_STATE_PREFIX` | `team-08/discord-service` |

Set these application variables in CircleCI:

| Variable | Runtime destination |
|---|---|
| `DISCORD_CLIENT_ID` | Secret Manager secret `discord-client-id` |
| `DISCORD_CLIENT_SECRET` | Secret Manager secret `discord-client-secret` |
| `DISCORD_BOT_TOKEN` | Secret Manager secret `discord-bot-token` |
| `DISCORD_GUILD_ID` | Secret Manager secret `discord-guild-id` |
| `SESSION_SECRET_KEY` | Secret Manager secret `session-secret-key` |

CircleCI reads those variables during deployment and adds them as new Secret Manager versions. Cloud Run then reads the values from Secret Manager at runtime.

### CircleCI Deployment Flow

The `deploy_infrastructure` job in `.circleci/config.yml` does this:

1. Authenticates to Google Cloud using `GCLOUD_SERVICE_KEY`.
2. Creates the Terraform state bucket if it does not exist.
3. Builds and pushes a new Docker image with Cloud Build.
4. Runs Terraform once to create Secret Manager secret containers.
5. Adds Secret Manager versions from CircleCI variables.
6. Runs Terraform again to apply the Cloud Run service, IAM, and image update.

## Useful Commands

```bash
# Check build status
gcloud builds list --region=us-east4 --project=ospsd8-discord --limit=5

# Stream build logs
gcloud beta builds log <BUILD_ID> --region=us-east4 --project=ospsd8-discord --stream

# Get service URL
gcloud run services describe discord-service --region=us-east4 --project=ospsd8-discord --format="value(status.url)"

# Add or rotate one Secret Manager value manually
printf '%s' "new-secret-value" | gcloud secrets versions add discord-bot-token \
  --project=ospsd8-discord \
  --data-file=-

# Test health endpoint
curl https://discord-service-122083288286.us-east4.run.app/health
```

## Environment Variables

Secret values are set in CircleCI and copied into Secret Manager during deployment. Do not commit secret values to source control.

| Variable | Description |
|---|---|
| `DISCORD_CLIENT_ID` | Discord OAuth application client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth application client secret |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_GUILD_ID` | Target Discord guild (server) ID |
| `DISCORD_REDIRECT_URI` | OAuth callback URL (`https://discord-service-122083288286.us-east4.run.app/auth/callback`) |
| `SESSION_SECRET_KEY` | Secret key for signed FastAPI session cookies |
| `OPENAI_API_KEY` | OpenAI API key for AI client integration |
| `GOOGLE_OAUTH_CREDENTIALS_PATH` | Path to Google OAuth credentials for calendar integration |
| `GOOGLE_OAUTH_TOKEN_PATH` | Path to Google OAuth token for calendar integration |
