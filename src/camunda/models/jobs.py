"""Job-related models."""

from __future__ import annotations

from typing import Any

from camunda.models.common import CamundaModel


class Job(CamundaModel):
    """An activated job."""

    job_key: str
    type: str
    process_instance_key: str
    process_definition_key: str
    process_definition_id: str
    process_definition_version: int
    element_id: str
    element_instance_key: str
    worker: str
    retries: int
    deadline: int
    variables: dict[str, Any] = {}
    tenant_id: str | None = None
    custom_headers: dict[str, str] = {}


class ActivateJobsRequest(CamundaModel):
    """Request to activate jobs."""

    type: str
    worker: str
    timeout: int = 300_000
    max_jobs_to_activate: int = 32
    fetch_variable: list[str] | None = None
    tenant_ids: list[str] | None = None
    request_timeout: int | None = None

    def to_api_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.type,
            "worker": self.worker,
            "timeout": self.timeout,
            "maxJobsToActivate": self.max_jobs_to_activate,
        }
        if self.fetch_variable:
            d["fetchVariable"] = self.fetch_variable
        if self.tenant_ids:
            d["tenantIds"] = self.tenant_ids
        if self.request_timeout is not None:
            d["requestTimeout"] = self.request_timeout
        return d
