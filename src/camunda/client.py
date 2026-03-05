"""Main Camunda client — single entry point for all API operations."""

from __future__ import annotations

import os
from typing import Any, Callable, Awaitable

import httpx

from camunda._http import HttpClient
from camunda.api.decisions import DecisionsApi
from camunda.api.deployments import DeploymentsApi
from camunda.api.incidents import IncidentsApi
from camunda.api.jobs import JobsApi
from camunda.api.messages import MessagesApi
from camunda.api.processes import ProcessesApi
from camunda.api.signals import SignalsApi
from camunda.api.tasks import TasksApi
from camunda.api.topology import TopologyApi
from camunda.api.variables import VariablesApi
from camunda.auth.base import NoAuth
from camunda.auth.basic import BasicAuth
from camunda.auth.bearer import BearerToken
from camunda.auth.oauth import OAuthCredentials
from camunda.config import CamundaConfig
from camunda.models.jobs import Job
from camunda.worker import WorkerManager


class CamundaClient:
    """Main client for the Camunda 8 REST API.

    Usage:
        client = CamundaClient(
            base_url="http://localhost:8080",
            auth=BasicAuth(username="demo", password="demo"),
        )
        instance = await client.processes.start(process_definition_id="my-process")
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth: httpx.Auth | None = None,
        config: CamundaConfig | None = None,
    ) -> None:
        if config is None:
            config = CamundaConfig(base_url=base_url or "http://localhost:8080")
        if auth is None:
            auth = NoAuth()

        self._config = config
        self._http = HttpClient(config=config, auth=auth)
        self._worker_manager = WorkerManager()

        self.processes = ProcessesApi(self._http)
        self.jobs = JobsApi(self._http)
        self.tasks = TasksApi(self._http)
        self.decisions = DecisionsApi(self._http)
        self.messages = MessagesApi(self._http)
        self.signals = SignalsApi(self._http)
        self.incidents = IncidentsApi(self._http)
        self.variables = VariablesApi(self._http)
        self.deployments = DeploymentsApi(self._http)
        self.topology = TopologyApi(self._http)

    @classmethod
    def from_env(cls) -> CamundaClient:
        """Create client from CAMUNDA_ environment variables."""
        config = CamundaConfig.from_env()
        auth_type = os.environ.get("CAMUNDA_AUTH_TYPE", "none").lower()

        auth: httpx.Auth
        if auth_type == "oauth":
            auth = OAuthCredentials.from_env()
        elif auth_type == "basic":
            auth = BasicAuth(
                username=os.environ["CAMUNDA_USERNAME"],
                password=os.environ["CAMUNDA_PASSWORD"],
            )
        elif auth_type == "bearer":
            auth = BearerToken(token=os.environ["CAMUNDA_TOKEN"])
        else:
            auth = NoAuth()

        return cls(config=config, auth=auth)

    def job_worker(
        self,
        task_type: str,
        *,
        timeout_ms: int = 300_000,
        max_jobs: int = 32,
        fetch_variables: list[str] | None = None,
        poll_interval: float = 0.5,
    ) -> Callable:
        """Decorator to register a job worker handler."""

        def decorator(
            func: Callable[[Job], Awaitable[dict[str, Any] | None]],
        ) -> Callable[[Job], Awaitable[dict[str, Any] | None]]:
            self._worker_manager.register(
                task_type=task_type,
                handler=func,
                timeout_ms=timeout_ms,
                max_jobs=max_jobs,
                fetch_variables=fetch_variables,
                poll_interval=poll_interval,
            )
            return func

        return decorator

    async def run_workers(self) -> None:
        """Start all registered job workers. Blocks until stop_workers() is called."""
        await self._worker_manager.run(self.jobs)

    def stop_workers(self) -> None:
        """Signal all workers to stop."""
        self._worker_manager.stop()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()
