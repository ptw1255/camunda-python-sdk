"""HTTP client wrapper with retry, auth, and error mapping."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from camunda.config import CamundaConfig
from camunda.exceptions import (
    AuthenticationError,
    CamundaError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

_STATUS_MAP: dict[int, type[CamundaError]] = {
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


class HttpClient:
    """Async HTTP client for the Camunda REST API."""

    def __init__(self, config: CamundaConfig, auth: httpx.Auth) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            auth=auth,
            timeout=config.request_timeout,
            headers={"content-type": "application/json"},
        )

    async def get(self, path: str, **kwargs: Any) -> Any:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        return await self._request("POST", path, json=json, **kwargs)

    async def patch(self, path: str, json: Any = None, **kwargs: Any) -> Any:
        return await self._request("PATCH", path, json=json, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> Any:
        return await self._request("DELETE", path, **kwargs)

    async def post_multipart(self, path: str, files: Any, **kwargs: Any) -> Any:
        """POST with multipart/form-data (for deployments)."""
        return await self._request("POST", path, files=files, **kwargs)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self._config.retry_count + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
                self._raise_for_status(response)
                if response.status_code == 204:
                    return None
                return response.json()
            except (httpx.ConnectError, httpx.TimeoutException, ServerError) as exc:
                last_exc = exc
                if attempt < self._config.retry_count:
                    delay = self._config.retry_backoff * (2**attempt)
                    await asyncio.sleep(delay)
                continue
            except CamundaError:
                raise
        raise last_exc  # type: ignore[misc]

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        detail = ""
        try:
            body = response.json()
            detail = body.get("message", str(body))
        except Exception:
            detail = response.text

        exc_class = _STATUS_MAP.get(response.status_code)
        if exc_class:
            raise exc_class(
                message=detail,
                status_code=response.status_code,
                detail=detail,
            )
        if response.status_code >= 500:
            raise ServerError(
                message=detail,
                status_code=response.status_code,
                detail=detail,
            )
        raise CamundaError(
            message=detail,
            status_code=response.status_code,
            detail=detail,
        )

    async def close(self) -> None:
        await self._client.aclose()
