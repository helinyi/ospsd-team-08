FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy workspace definition and lock file first for layer caching
COPY pyproject.toml uv.lock ./

# Copy all workspace component packages
COPY components/chat_client_api/ components/chat_client_api/
COPY components/discord_client_impl/ components/discord_client_impl/
COPY components/discord_service/ components/discord_service/
COPY components/discord_service_api_client/ components/discord_service_api_client/

# Install production dependencies only (no dev group)
RUN uv sync --all-packages --no-dev --frozen

# Cloud Run sets PORT env var; default to 8080
ENV PORT=8080
ENV HOST=0.0.0.0

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "discord_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
