# CS-GY-9223 Open Source — Team 8

A modular chat client architecture consisting of:

- A provider-agnostic chat interface (`chat_client_api`)
- A Discord implementation (`discord_client_impl`)

This project demonstrates clean component separation, interface purity, and extensibility for future providers.

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

## Prerequisites

- Python 3.10 or higher  
- [uv](https://docs.astral.sh/uv/) package manager  

Install uv (if not installed):

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

## Installation
```bash
# Clone the repository
git clone <Our-REPO-URL>
cd ospsd-team-08

# Install dependencies
uv sync

# Install with all dependencies (dev + docs)
uv sync --all-extras
```


## Development
```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy components tests
```

## Documentation

```bash
# Build and serve documentation locally:
uv run mkdocs serve

# Then open:
http://127.0.0.1:8000
```


## Project Structure
```
.
├── components/                # Interface + implementation components
│   ├── chat_client_api/       # Abstract chat client interface
│   └── discord_client_impl/   # Discord implementation (HW1 minimal stub)
├── tests/                     # Test suite
├── docs/                      # MkDocs documentation
├── contributing.md            # Contribution guide
├── design.md                  # Design document
├── mkdocs.yml                 # MkDocs configuration
├── pyproject.toml             # Project configuration
└── README.md
```

## Dependency Injection Usage

```python
import discord_client_impl  # injects factory
from chat_client_api import get_client

client = get_client()
```


## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

