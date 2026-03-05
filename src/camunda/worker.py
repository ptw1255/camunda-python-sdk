"""Job worker decorator and polling loop."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from camunda.models.jobs import Job

logger = logging.getLogger("camunda.worker")


@dataclass
class WorkerRegistration:
    """A registered job worker handler."""

    task_type: str
    handler: Callable[[Job], Awaitable[dict[str, Any] | None]]
    timeout_ms: int = 300_000
    max_jobs: int = 32
    fetch_variables: list[str] | None = None
    poll_interval: float = 0.5


class WorkerManager:
    """Manages job worker polling and dispatch."""

    def __init__(self) -> None:
        self._registrations: list[WorkerRegistration] = []
        self._running = False

    def register(
        self,
        task_type: str,
        handler: Callable[[Job], Awaitable[dict[str, Any] | None]],
        timeout_ms: int = 300_000,
        max_jobs: int = 32,
        fetch_variables: list[str] | None = None,
        poll_interval: float = 0.5,
    ) -> None:
        self._registrations.append(
            WorkerRegistration(
                task_type=task_type,
                handler=handler,
                timeout_ms=timeout_ms,
                max_jobs=max_jobs,
                fetch_variables=fetch_variables,
                poll_interval=poll_interval,
            )
        )

    async def run(self, jobs_api: Any) -> None:
        """Start polling for all registered workers."""
        self._running = True
        tasks = [self._poll_loop(reg, jobs_api) for reg in self._registrations]
        await asyncio.gather(*tasks)

    def stop(self) -> None:
        self._running = False

    async def _poll_loop(self, reg: WorkerRegistration, jobs_api: Any) -> None:
        worker_name = f"camunda-python-{reg.task_type}"
        while self._running:
            try:
                jobs = await jobs_api.activate(
                    type=reg.task_type,
                    worker=worker_name,
                    timeout=reg.timeout_ms,
                    max_jobs=reg.max_jobs,
                    fetch_variables=reg.fetch_variables,
                )
                for job in jobs:
                    try:
                        result = await reg.handler(job)
                        await jobs_api.complete(job.job_key, variables=result)
                    except Exception as exc:
                        logger.exception("Job %s failed: %s", job.job_key, exc)
                        await jobs_api.fail(
                            job.job_key,
                            retries=max(0, job.retries - 1),
                            error_message=str(exc),
                        )
            except Exception as exc:
                logger.exception("Poll failed for %s: %s", reg.task_type, exc)

            await asyncio.sleep(reg.poll_interval)
