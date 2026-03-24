## Description

Briefly describe the purpose of this pull request.

* What changes were made?
* Why are these changes needed?

---

## Type of Change

Please select the relevant option(s):

* [ ] Feature – add a new module/functionality (e.g., new model, API, data processing)
* [ ] Bug Fix – fix an error or incorrect behavior
* [ ] Refactoring – improve code structure/readability (no functionality change)
* [ ] Documentation – update README, comments, or project documentation
* [ ] Test – add or update unit tests / test scripts
* [ ] Configuration / Setup – environment setup, dependencies, project structure, GitHub config
* [ ] Performance Improvement – optimize speed, memory, or efficiency
* [ ] Other (please describe below)

---

## Changes Summary

Main updates in this PR:

### Cloud Deployment (helinyi)
* Deployed FastAPI service to Google Cloud Run (`https://discord-service-122083288286.us-east4.run.app`)
* Created `Dockerfile`, `.dockerignore`, and `cloudbuild.yaml` for containerized deployment
* Set up Cloud Build trigger — auto-deploys on every push to `hw-2` from GitHub
* Configured GCP project `ospsd8-discord` (IAM roles, Secret Manager, Artifact Registry)
* Environment variables stored securely via Cloud Run secrets — not in source control
* See [CLOUDRUN.md](../CLOUDRUN.md) for full setup details

### Auto-Generated Client (helinyi)
* Generated `discord_service_api_client` using `openapi-python-client` from deployed service's `/openapi.json`
* Type-safe Python client for all endpoints: health, auth, channels, messages
* Integrated into `uv` workspace with `hatchling` build backend
* See [component README](../components/discord_service_api_client/README.md) for usage

---

## Evidence / Validation

Provide evidence that your changes work.

Examples:

* Screenshots
* Program output
* Test results
* Logs

```
$ curl https://discord-service-122083288286.us-east4.run.app/health
{"status":"ok"}

CircleCI Pipeline #67: lint ✓ test ✓
Cloud Build: auto-deploy from GitHub trigger working
OpenAPI spec: https://discord-service-122083288286.us-east4.run.app/openapi.json
```

---

## Checklist

* [ ] Code runs without errors
* [ ] No unnecessary files included
* [ ] Self-review completed
* [ ] Follows project structure/style
* [ ] Documentation updated (if needed)

---

## Related Issue

Closes: #
