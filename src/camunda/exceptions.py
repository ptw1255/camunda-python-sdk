"""Camunda SDK exception hierarchy."""

from __future__ import annotations


class CamundaError(Exception):
    """Base exception for all Camunda SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        detail: str | None = None,
        instance: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.instance = instance


class AuthenticationError(CamundaError):
    """401/403 — authentication or authorization failure."""


class NotFoundError(CamundaError):
    """404 — resource not found."""


class ConflictError(CamundaError):
    """409 — resource state conflict (e.g., task already completed)."""


class RateLimitError(CamundaError):
    """429 — rate limit exceeded."""


class ServerError(CamundaError):
    """5xx — server-side error."""


class JobTimeoutError(CamundaError):
    """Job worker failed to complete within the timeout."""
