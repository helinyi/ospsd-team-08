#!/usr/bin/env bash
# Pull Google OAuth credentials + token from Secret Manager into the repo root.
# Skips files that already exist; pass --force to overwrite (e.g. after rotation).
#
# Prerequisite: `gcloud auth login` with an account that has
# roles/secretmanager.secretAccessor on the ospsd8-discord project.

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-ospsd8-discord}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

force=0
for arg in "$@"; do
  case "${arg}" in
    -f|--force) force=1 ;;
    -h|--help)
      sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'
      echo
      echo "Usage: $0 [--force]"
      exit 0
      ;;
    *)
      echo "Unknown argument: ${arg}" >&2
      exit 1
      ;;
  esac
done

fetch() {
  local secret_id="$1"
  local out_path="$2"

  if [[ -s "${out_path}" && "${force}" -eq 0 ]]; then
    echo "Skipping ${out_path} (already exists; use --force to overwrite)"
    return 0
  fi

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
