"""Signals API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient


class SignalsApi:
    """Client for signal operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def broadcast(
        self,
        *,
        signal_name: str,
        variables: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"signalName": signal_name}
        if variables:
            payload["variables"] = variables
        if tenant_id:
            payload["tenantId"] = tenant_id
        return await self._http.post("/v2/signals/broadcast", json=payload)
