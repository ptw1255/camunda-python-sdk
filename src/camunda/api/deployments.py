"""Deployments API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from camunda._http import HttpClient


class DeploymentResult:
    """Result of a deployment."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.deployment_key: str = data.get("deploymentKey", "")
        self.deployments: list[dict[str, Any]] = data.get("deployments", [])
        self.tenant_id: str | None = data.get("tenantId")


class DeploymentsApi:
    """Client for deployment operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def deploy(self, *resource_paths: str | Path) -> DeploymentResult:
        files = []
        for path in resource_paths:
            p = Path(path)
            files.append(("resources", (p.name, p.read_bytes())))
        data = await self._http.post_multipart("/v2/deployments", files=files)
        return DeploymentResult(data)
