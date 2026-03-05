"""OAuth2 client credentials authentication with token caching."""

from __future__ import annotations

import os
import time

import httpx


class OAuthCredentials(httpx.Auth):
    """OAuth2 client credentials flow with automatic token refresh."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str = "https://login.cloud.camunda.io/oauth/token",
        audience: str = "zeebe.camunda.io",
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._audience = audience
        self._cached_token: str | None = None
        self._token_expiry: float = 0.0

    @classmethod
    def from_env(cls) -> OAuthCredentials:
        """Create from CAMUNDA_ environment variables."""
        return cls(
            client_id=os.environ["CAMUNDA_CLIENT_ID"],
            client_secret=os.environ["CAMUNDA_CLIENT_SECRET"],
            token_url=os.environ.get(
                "CAMUNDA_TOKEN_URL", "https://login.cloud.camunda.io/oauth/token"
            ),
            audience=os.environ.get("CAMUNDA_AUDIENCE", "zeebe.camunda.io"),
        )

    async def get_token(self) -> str:
        """Get a valid access token, refreshing if expired."""
        if self._cached_token and time.monotonic() < self._token_expiry:
            return self._cached_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "audience": self._audience,
                },
            )
            response.raise_for_status()
            data = response.json()

        self._cached_token = data["access_token"]
        self._token_expiry = time.monotonic() + data.get("expires_in", 3600) - 60
        return self._cached_token

    def auth_flow(self, request: httpx.Request):
        if self._cached_token:
            request.headers["authorization"] = f"Bearer {self._cached_token}"
        yield request
