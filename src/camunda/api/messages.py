"""Messages API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.messages import MessageCorrelationResult, MessagePublicationResult


class MessagesApi:
    """Client for message operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def publish(
        self,
        *,
        name: str,
        correlation_key: str,
        variables: dict[str, Any] | None = None,
        time_to_live: int | None = None,
        message_id: str | None = None,
        tenant_id: str | None = None,
    ) -> MessagePublicationResult:
        payload: dict[str, Any] = {"name": name, "correlationKey": correlation_key}
        if variables:
            payload["variables"] = variables
        if time_to_live is not None:
            payload["timeToLive"] = time_to_live
        if message_id:
            payload["messageId"] = message_id
        if tenant_id:
            payload["tenantId"] = tenant_id
        data = await self._http.post("/v2/messages/publication", json=payload)
        return MessagePublicationResult.model_validate(data)

    async def correlate(
        self,
        *,
        name: str,
        correlation_key: str,
        variables: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> MessageCorrelationResult:
        payload: dict[str, Any] = {"name": name, "correlationKey": correlation_key}
        if variables:
            payload["variables"] = variables
        if tenant_id:
            payload["tenantId"] = tenant_id
        data = await self._http.post("/v2/messages/correlation", json=payload)
        return MessageCorrelationResult.model_validate(data)
