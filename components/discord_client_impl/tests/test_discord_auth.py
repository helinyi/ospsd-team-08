"""Unit tests for DiscordAuthenticator and DiscordOAuthHandler."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from discord_client_impl.auth import DiscordAuthenticator, DiscordOAuthHandler


# ─── DiscordAuthenticator tests ───────────────────────────────────────────────
def test_from_env_raises_when_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raises RuntimeError when DISCORD_BOT_TOKEN is not set."""
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_BOT_TOKEN"):
        DiscordAuthenticator.from_env()


def test_from_env_succeeds_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns an authenticator when the env var is set."""
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token-123")
    auth = DiscordAuthenticator.from_env()
    assert auth is not None


def test_get_headers_returns_correct_format(monkeypatch: pytest.MonkeyPatch) -> None:
    """Authorization header uses the Bot scheme with the token."""
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "my-secret-token")
    auth = DiscordAuthenticator.from_env()
    headers = auth.get_headers()
    assert headers["Authorization"] == "Bot my-secret-token"
    assert headers["Content-Type"] == "application/json"


def test_validate_raises_on_401() -> None:
    """Raises RuntimeError when Discord returns 401 Unauthorized."""
    auth = DiscordAuthenticator(token="bad-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.ok = False
    with (
        patch("discord_client_impl.auth.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="401"),
    ):
        auth.validate()


def test_validate_raises_on_other_error() -> None:
    """Raises RuntimeError when Discord returns a non-200, non-401 status."""
    auth = DiscordAuthenticator(token="some-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.ok = False
    with (
        patch("discord_client_impl.auth.requests.get", return_value=mock_response),
        pytest.raises(RuntimeError, match="500"),
    ):
        auth.validate()


def test_validate_succeeds() -> None:
    """Does not raise when Discord returns 200 OK."""
    auth = DiscordAuthenticator(token="valid-token")  # noqa: S106
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    with patch("discord_client_impl.auth.requests.get", return_value=mock_response):
        auth.validate()  # Should not raise


def test_validate_raises_on_request_exception() -> None:
    """Raises RuntimeError when a network error occurs during validate."""
    auth = DiscordAuthenticator(token="valid-token")  # noqa: S106
    with (
        patch(
            "discord_client_impl.auth.requests.get",
            side_effect=requests.RequestException("connection error"),
        ),
        pytest.raises(RuntimeError, match="connection error"),
    ):
        auth.validate()


# ─── DiscordOAuthHandler tests ───────────────────────────────────────────────
@pytest.fixture
def oauth_handler(monkeypatch: pytest.MonkeyPatch) -> DiscordOAuthHandler:
    """Create a DiscordOAuthHandler from env vars."""
    monkeypatch.setenv("DISCORD_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("DISCORD_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv(
        "DISCORD_REDIRECT_URI", "http://localhost:8000/auth/callback"
    )
    return DiscordOAuthHandler.from_env()


def test_oauth_from_env_raises_when_client_id_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raises RuntimeError when DISCORD_CLIENT_ID is not set."""
    monkeypatch.delenv("DISCORD_CLIENT_ID", raising=False)
    monkeypatch.setenv("DISCORD_CLIENT_SECRET", "secret")
    with pytest.raises(RuntimeError, match="DISCORD_CLIENT_ID"):
        DiscordOAuthHandler.from_env()


def test_oauth_from_env_raises_when_client_secret_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raises RuntimeError when DISCORD_CLIENT_SECRET is not set."""
    monkeypatch.setenv("DISCORD_CLIENT_ID", "client-id")
    monkeypatch.delenv("DISCORD_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_CLIENT_SECRET"):
        DiscordOAuthHandler.from_env()


def test_oauth_from_env_succeeds(oauth_handler: DiscordOAuthHandler) -> None:
    """Returns a handler when all env vars are set."""
    assert oauth_handler is not None


def test_get_authorization_url_contains_client_id(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """Authorization URL contains the client ID."""
    url = oauth_handler.get_authorization_url()
    assert "test-client-id" in url
    assert "https://discord.com/oauth2/authorize" in url


def test_get_authorization_url_contains_redirect_uri(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """Authorization URL contains the redirect URI."""
    url = oauth_handler.get_authorization_url()
    assert "localhost:8000" in url


def test_get_authorization_url_contains_scopes(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """Authorization URL contains required scopes."""
    url = oauth_handler.get_authorization_url()
    assert "identify" in url
    assert "guilds" in url


def test_exchange_code_returns_access_token(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """exchange_code returns the access token from the response."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"access_token": "my-access-token"}

    with patch(
        "discord_client_impl.auth.requests.post", return_value=mock_response
    ):
        token = oauth_handler.exchange_code("auth-code-123")

    assert token == "my-access-token" # noqa: S105 - test assertion value, not a real token


def test_exchange_code_raises_on_failure(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """exchange_code raises RuntimeError when the API returns non-200."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400

    with (
        patch(
            "discord_client_impl.auth.requests.post", return_value=mock_response
        ),
        pytest.raises(RuntimeError, match="400"),
    ):
        oauth_handler.exchange_code("bad-code")


def test_exchange_code_raises_on_request_exception(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """exchange_code raises RuntimeError on network error."""
    with (
        patch(
            "discord_client_impl.auth.requests.post",
            side_effect=requests.RequestException("network error"),
        ),
        pytest.raises(RuntimeError, match="network error"),
    ):
        oauth_handler.exchange_code("any-code")


def test_get_oauth_headers_returns_bearer_format(
    oauth_handler: DiscordOAuthHandler,
) -> None:
    """OAuth headers use Bearer scheme with the access token."""
    headers = DiscordOAuthHandler.get_oauth_headers("my-token")
    assert headers["Authorization"] == "Bearer my-token"
    assert headers["Content-Type"] == "application/json"
