# Google Cloud Run Deployment

**Project:** `ospsd8-discord`
**Region:** `us-east4`
**Service URL:** `https://discord-service-122083288286.us-east4.run.app`

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- Authenticated with `gcloud auth login`

## Setup Commands

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

### 6. Create Cloud Build Trigger

Auto-deploys on every push to the `hw-2` branch:

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

## Useful Commands

```bash
# Check build status
gcloud builds list --region=us-east4 --project=ospsd8-discord --limit=5

# Stream build logs
gcloud beta builds log <BUILD_ID> --region=us-east4 --project=ospsd8-discord --stream

# Get service URL
gcloud run services describe discord-service --region=us-east4 --project=ospsd8-discord --format="value(status.url)"

# Update environment variables
gcloud run services update discord-service --region=us-east4 --project=ospsd8-discord \
  --set-env-vars "DISCORD_CLIENT_ID=xxx,DISCORD_CLIENT_SECRET=xxx,DISCORD_BOT_TOKEN=xxx,DISCORD_GUILD_ID=xxx,DISCORD_REDIRECT_URI=https://discord-service-122083288286.us-east4.run.app/auth/callback"

# Test health endpoint
curl https://discord-service-122083288286.us-east4.run.app/health
```

## Environment Variables

Set these via Cloud Run (Console or CLI) — never commit secrets to source control:

| Variable | Description |
|---|---|
| `DISCORD_CLIENT_ID` | Discord OAuth application client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth application client secret |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_GUILD_ID` | Target Discord guild (server) ID |
| `DISCORD_REDIRECT_URI` | OAuth callback URL (`https://discord-service-122083288286.us-east4.run.app/auth/callback`) |
