"""Variables API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.common import SearchResult, CamundaModel


class Variable(CamundaModel):
    """A process variable."""

    variable_key: str | None = None
    name: str | None = None
    value: Any = None
    process_instance_key: str | None = None
    scope_key: str | None = None
    tenant_id: str | None = None


class VariablesApi:
    """Client for variable operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def search(
        self,
        *,
        filter: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> SearchResult[Variable]:
        payload: dict[str, Any] = {}
        if filter:
            payload["filter"] = filter
        payload["page"] = {"limit": limit}
        data = await self._http.post("/v2/variables/search", json=payload)
        return SearchResult[Variable].model_validate(data)

    async def get(self, variable_key: str) -> Variable:
        data = await self._http.get(f"/v2/variables/{variable_key}")
        return Variable.model_validate(data)
