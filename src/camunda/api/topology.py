"""Topology API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient


class TopologyApi:
    """Client for cluster topology."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(self) -> dict[str, Any]:
        return await self._http.get("/v2/topology")
