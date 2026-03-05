"""Jobs API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.jobs import Job


class JobsApi:
    """Client for job operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def activate(
        self,
        *,
        type: str,
        worker: str,
        timeout: int = 300_000,
        max_jobs: int = 32,
        fetch_variables: list[str] | None = None,
        request_timeout: int | None = None,
        tenant_ids: list[str] | None = None,
    ) -> list[Job]:
        payload: dict[str, Any] = {
            "type": type,
            "worker": worker,
            "timeout": timeout,
            "maxJobsToActivate": max_jobs,
        }
        if fetch_variables:
            payload["fetchVariable"] = fetch_variables
        if request_timeout is not None:
            payload["requestTimeout"] = request_timeout
        if tenant_ids:
            payload["tenantIds"] = tenant_ids
        data = await self._http.post("/v2/jobs/activation", json=payload)
        return [Job.model_validate(j) for j in data.get("jobs", [])]

    async def complete(self, job_key: str, *, variables: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {}
        if variables:
            payload["variables"] = variables
        await self._http.post(f"/v2/jobs/{job_key}/completion", json=payload)

    async def fail(
        self,
        job_key: str,
        *,
        retries: int,
        error_message: str = "",
        retry_back_off: int = 0,
    ) -> None:
        await self._http.post(
            f"/v2/jobs/{job_key}/failure",
            json={
                "retries": retries,
                "errorMessage": error_message,
                "retryBackOff": retry_back_off,
            },
        )

    async def throw_error(
        self,
        job_key: str,
        *,
        error_code: str,
        error_message: str = "",
        variables: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"errorCode": error_code, "errorMessage": error_message}
        if variables:
            payload["variables"] = variables
        await self._http.post(f"/v2/jobs/{job_key}/error", json=payload)
