#!/usr/bin/env bash
# Pull Google OAuth credentials + token from Secret Manager into the repo root.
# Required once per dev machine (and again whenever the secrets are rotated).
#
# Prerequisite: `gcloud auth login` with an account that has
# roles/secretmanager.secretAccessor on the ospsd8-discord project.

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-ospsd8-discord}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fetch() {
  local secret_id="$1"
  local out_path="$2"
  echo "Fetching ${secret_id} -> ${out_path}"
  gcloud secrets versions access latest \
    --secret="${secret_id}" \
    --project="${PROJECT_ID}" \
    > "${out_path}"
  chmod 600 "${out_path}"
}

fetch "google-oauth-credentials" "${REPO_ROOT}/credentials.json"
fetch "google-oauth-token"       "${REPO_ROOT}/token.json"

echo
echo "Done. credentials.json and token.json are in the repo root (gitignored)."
echo "You can now run the service locally and hit /calendar/* endpoints."
