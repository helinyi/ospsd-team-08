# CS-GY-9223 Open Source — Team 8

A modular chat client architecture built on Discord, demonstrating clean component separation, dependency injection, OAuth 2.0, and microservice deployment.

---

## Team

**Team name:** Team 8

**Members:**

- Jia Hao Lin — jl12846
- Aaron Wu — aw3950
- Zhiqi Zhao — zz10677
- Linyi He — lh1505
- Calico Wang — jw8221

**Course staff (collaborators to add):**

- adithyab-20
- ivanearisty
- AranyaAryaman

---

## Architecture
```
chat_client_api          ← Abstract interface (provider-agnostic)
        ↑
discord_client_impl      ← Concrete implementation (real Discord API + OAuth 2.0)
        ↑
discord_service          ← FastAPI microservice (deployed to Google Cloud Run)
        ↑
discord_service_api_client  ← Auto-generated type-safe HTTP client
        ↑
discord_adapter          ← Adapter implementing ChatClient via the service
```

Both `discord_client_impl` and `discord_adapter` implement the same `ChatClient` interface — swapping between them requires no changes to consumer code.

---

## Live Deployment

Service is live at:
```
https://discord-service-122083288286.us-east4.run.app
```

API docs:
```
https://discord-service-122083288286.us-east4.run.app/docs
```

---

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

Install uv (if not installed):
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

---

## Installation
```bash
# Clone the repository
git clone <Our-REPO-URL>
cd ospsd-team-08

# Install all dependencies
uv sync --all-packages
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:
```
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET_KEY=any-random-string
```

---

## Development
```bash
# Run all tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy components/
```

---

## Infrastructure as Code

Infrastructure is managed with Terraform in `infra/terraform`.

Terraform imports and manages the existing Google Cloud resources:

- Cloud Run service: `discord-service`
- Artifact Registry repository: `cloud-run-source-deploy`
- CircleCI Terraform deployer service account and IAM
- Secret Manager secret containers
- Cloud Run runtime service account and IAM

CircleCI runs the deployment workflow. Store deployment and application secrets in CircleCI project environment variables or a CircleCI context. During deployment, CircleCI copies those values into Google Secret Manager so Cloud Run reads secrets at runtime.

Useful local checks:

```bash
terraform fmt -check -recursive infra/terraform
terraform -chdir=infra/terraform init -backend=false
terraform -chdir=infra/terraform validate
```

---

## Running the Service Locally
```bash
uv run uvicorn discord_service.main:app --reload
```

Then visit:
- `http://localhost:8000/health` — health check
- `http://localhost:8000/docs` — API documentation
- `http://localhost:8000/auth/login` — start OAuth 2.0 flow

---

## Dependency Injection Usage
```python
# Using local library
import discord_client_impl
from chat_client_api import get_client

client = get_client()
channels = client.get_channels()

# Using remote service (via adapter)
import discord_adapter
from chat_client_api import get_client

client = get_client()
channels = client.get_channels()  # same code, different implementation
```

---

## Documentation
```bash
# Build and serve documentation locally
uv run mkdocs serve

# Then open:
http://127.0.0.1:8000
```

---

## Project Structure
```
.
├── components/
│   ├── discord_client_impl/       # Discord implementation + OAuth 2.0
│   ├── discord_service/           # FastAPI microservice
│   ├── discord_service_api_client/ # Auto-generated API client
│   └── discord_adapter/           # Service client adapter
├── tests/
│   ├── e2e/                       # End-to-end tests
│   └── integration/               # Integration tests
├── infra/
│   └── terraform/                  # Google Cloud Run IaC
├── docs/                          # MkDocs documentation
├── contributing.md
├── design.md
├── mkdocs.yml
├── pyproject.toml
└── README.md
```
Note: `chat_client_api` is now consumed as an external git dependency from the shared vertical API repo.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
