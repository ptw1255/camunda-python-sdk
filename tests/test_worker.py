import asyncio

import httpx
import pytest
import respx

from camunda import CamundaClient
from camunda.auth.base import NoAuth
from camunda.models.jobs import Job


@respx.mock
@pytest.mark.asyncio
async def test_job_worker_decorator():
    client = CamundaClient(base_url="http://localhost:8080", auth=NoAuth())

    results = []

    @client.job_worker("test-task", timeout_ms=10000, poll_interval=0.05)
    async def handler(job: Job) -> dict:
        results.append(job.job_key)
        return {"processed": True}

    call_count = 0

    def activation_side_effect(request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(200, json={
                "jobs": [{
                    "jobKey": "42",
                    "type": "test-task",
                    "processInstanceKey": "1",
                    "processDefinitionKey": "2",
                    "processDefinitionId": "test",
                    "processDefinitionVersion": 1,
                    "elementId": "task1",
                    "elementInstanceKey": "3",
                    "worker": "test-worker",
                    "retries": 3,
                    "deadline": 9999999999999,
                    "variables": {},
                    "tenantId": "<default>",
                }]
            })
        return httpx.Response(200, json={"jobs": []})

    respx.post("http://localhost:8080/v2/jobs/activation").mock(
        side_effect=activation_side_effect
    )
    respx.post("http://localhost:8080/v2/jobs/42/completion").mock(
        return_value=httpx.Response(204)
    )

    task = asyncio.create_task(client.run_workers())
    await asyncio.sleep(0.3)
    client.stop_workers()
    await task

    assert results == ["42"]
