"""User tasks API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.common import SearchResult, SortOrder
from camunda.models.tasks import UserTask


class TasksApi:
    """Client for user task operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def search(
        self,
        *,
        filter: dict[str, Any] | None = None,
        sort: list[SortOrder] | None = None,
        limit: int = 50,
    ) -> SearchResult[UserTask]:
        payload: dict[str, Any] = {}
        if filter:
            payload["filter"] = filter
        if sort:
            payload["sort"] = [{"field": s.field, "order": s.order} for s in sort]
        payload["page"] = {"limit": limit}
        data = await self._http.post("/v2/user-tasks/search", json=payload)
        return SearchResult[UserTask].model_validate(data)

    async def get(self, task_key: str) -> UserTask:
        data = await self._http.get(f"/v2/user-tasks/{task_key}")
        return UserTask.model_validate(data)

    async def complete(self, task_key: str, *, variables: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {}
        if variables:
            payload["variables"] = variables
        await self._http.post(f"/v2/user-tasks/{task_key}/completion", json=payload)

    async def assign(self, task_key: str, *, assignee: str, allow_override: bool = True) -> None:
        await self._http.patch(
            f"/v2/user-tasks/{task_key}/assign",
            json={"assignee": assignee, "allowOverrideAssignment": allow_override},
        )

    async def unassign(self, task_key: str) -> None:
        await self._http.patch(f"/v2/user-tasks/{task_key}/unassign", json={})
