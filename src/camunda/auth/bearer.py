"""Bearer token authentication."""

from __future__ import annotations

import httpx


class BearerToken(httpx.Auth):
    """Pre-obtained bearer token authentication."""

    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(self, request: httpx.Request):
        request.headers["authorization"] = f"Bearer {self._token}"
        yield request
