"""Cookie-based session authentication."""

from __future__ import annotations

import httpx


class CookieAuth(httpx.Auth):
    """Cookie/session-based authentication."""

    def __init__(self, cookie_name: str, cookie_value: str) -> None:
        self._cookie_name = cookie_name
        self._cookie_value = cookie_value

    def auth_flow(self, request: httpx.Request):
        request.headers["cookie"] = f"{self._cookie_name}={self._cookie_value}"
        yield request
