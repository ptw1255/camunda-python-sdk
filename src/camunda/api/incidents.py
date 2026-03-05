"""Incidents API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.common import SearchResult, SortOrder
from camunda.models.incidents import Incident


class IncidentsApi:
    """Client for incident operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def search(
        self,
        *,
        filter: dict[str, Any] | None = None,
        sort: list[SortOrder] | None = None,
        limit: int = 50,
    ) -> SearchResult[Incident]:
        payload: dict[str, Any] = {}
        if filter:
            payload["filter"] = filter
        if sort:
            payload["sort"] = [{"field": s.field, "order": s.order} for s in sort]
        payload["page"] = {"limit": limit}
        data = await self._http.post("/v2/incidents/search", json=payload)
        return SearchResult[Incident].model_validate(data)

    async def get(self, incident_key: str) -> Incident:
        data = await self._http.get(f"/v2/incidents/{incident_key}")
        return Incident.model_validate(data)

    async def resolve(self, incident_key: str) -> None:
        await self._http.post(f"/v2/incidents/{incident_key}/resolution", json={})
