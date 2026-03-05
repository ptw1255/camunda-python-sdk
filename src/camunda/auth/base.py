"""Base auth strategy protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class AuthStrategy(Protocol):
    """Protocol for authentication strategies."""

    def auth_flow(self, request: httpx.Request) -> httpx.Request:
        """Apply auth to a request. Used as httpx auth flow."""
        ...


class NoAuth(httpx.Auth):
    """No authentication. For mTLS or dev environments."""

    def auth_flow(self, request: httpx.Request):
        yield request
