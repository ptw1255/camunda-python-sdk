"""Process definitions and instances API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.common import SearchResult, SortOrder
from camunda.models.processes import ProcessInstance


class ProcessesApi:
    """Client for process definition and instance operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def start(
        self,
        *,
        process_definition_id: str | None = None,
        process_definition_key: str | None = None,
        variables: dict[str, Any] | None = None,
        await_completion: bool = False,
        tenant_id: str | None = None,
    ) -> ProcessInstance:
        payload: dict[str, Any] = {}
        if process_definition_id:
            payload["processDefinitionId"] = process_definition_id
        if process_definition_key:
            payload["processDefinitionKey"] = process_definition_key
        if variables:
            payload["variables"] = variables
        if await_completion:
            payload["awaitCompletion"] = True
        if tenant_id:
            payload["tenantId"] = tenant_id
        data = await self._http.post("/v2/process-instances", json=payload)
        return ProcessInstance.model_validate(data)

    async def get(self, process_instance_key: str) -> ProcessInstance:
        data = await self._http.get(f"/v2/process-instances/{process_instance_key}")
        return ProcessInstance.model_validate(data)

    async def cancel(self, process_instance_key: str) -> None:
        await self._http.post(f"/v2/process-instances/{process_instance_key}/cancellation", json={})

    async def search(
        self,
        *,
        filter: dict[str, Any] | None = None,
        sort: list[SortOrder] | None = None,
        limit: int = 50,
    ) -> SearchResult[ProcessInstance]:
        payload: dict[str, Any] = {}
        if filter:
            payload["filter"] = filter
        if sort:
            payload["sort"] = [{"field": s.field, "order": s.order} for s in sort]
        payload["page"] = {"limit": limit}
        data = await self._http.post("/v2/process-instances/search", json=payload)
        return SearchResult[ProcessInstance].model_validate(data)

    async def get_xml(self, process_definition_key: str) -> str:
        data = await self._http.get(f"/v2/process-definitions/{process_definition_key}/xml")
        return data
