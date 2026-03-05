"""Camunda SDK configuration with Pydantic validation."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field


class CamundaConfig(BaseModel):
    """Configuration for the Camunda SDK."""

    base_url: str = Field(description="Camunda cluster REST API base URL")
    request_timeout: float = Field(default=30.0, description="HTTP request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on transient failures")
    retry_backoff: float = Field(default=1.0, description="Exponential backoff base in seconds")
    worker_poll_interval: float = Field(
        default=0.5, description="Job worker poll interval in seconds"
    )
    worker_max_jobs: int = Field(default=32, description="Max jobs per activation poll")
    worker_default_timeout_ms: int = Field(
        default=300_000, description="Default job timeout in ms"
    )
    tenant_id: str | None = Field(default=None, description="Default tenant ID")

    @classmethod
    def from_env(cls, **overrides: Any) -> CamundaConfig:
        """Create config from CAMUNDA_ environment variables."""
        return cls(
            base_url=os.environ.get("CAMUNDA_BASE_URL", overrides.get("base_url", "")),
            request_timeout=float(
                os.environ.get("CAMUNDA_REQUEST_TIMEOUT", overrides.get("request_timeout", 30.0))
            ),
            retry_count=int(
                os.environ.get("CAMUNDA_RETRY_COUNT", overrides.get("retry_count", 3))
            ),
            retry_backoff=float(
                os.environ.get("CAMUNDA_RETRY_BACKOFF", overrides.get("retry_backoff", 1.0))
            ),
            worker_poll_interval=float(
                os.environ.get(
                    "CAMUNDA_WORKER_POLL_INTERVAL",
                    overrides.get("worker_poll_interval", 0.5),
                )
            ),
            worker_max_jobs=int(
                os.environ.get("CAMUNDA_WORKER_MAX_JOBS", overrides.get("worker_max_jobs", 32))
            ),
            tenant_id=os.environ.get("CAMUNDA_TENANT_ID", overrides.get("tenant_id")),
        )
