"""Basic authentication."""

from __future__ import annotations

import base64

import httpx


class BasicAuth(httpx.Auth):
    """HTTP Basic authentication."""

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password

    def auth_flow(self, request: httpx.Request):
        credentials = base64.b64encode(
            f"{self._username}:{self._password}".encode()
        ).decode("ascii")
        request.headers["authorization"] = f"Basic {credentials}"
        yield request
