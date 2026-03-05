import httpx
import pytest
import respx

from camunda._http import HttpClient
from camunda.api.tasks import TasksApi
from camunda.auth.base import NoAuth
from camunda.config import CamundaConfig


@pytest.fixture
def http_client():
    config = CamundaConfig(base_url="http://localhost:8080", retry_count=0)
    return HttpClient(config=config, auth=NoAuth())


@pytest.fixture
def tasks_api(http_client):
    return TasksApi(http_client)


@respx.mock
@pytest.mark.asyncio
async def test_search_tasks(tasks_api):
    respx.post("http://localhost:8080/v2/user-tasks/search").mock(
        return_value=httpx.Response(200, json={
            "items": [{
                "userTaskKey": "555",
                "state": "CREATED",
                "assignee": "jane",
                "candidateGroups": ["reviewers"],
                "candidateUsers": [],
                "processInstanceKey": "456",
                "processDefinitionId": "loan-approval",
                "elementId": "review-task",
                "creationDate": "2026-03-04T12:00:00Z",
                "tenantId": "<default>",
            }],
            "page": {"totalItems": 1},
        })
    )
    result = await tasks_api.search(filter={"state": "CREATED"})
    assert len(result.items) == 1
    assert result.items[0].assignee == "jane"


@respx.mock
@pytest.mark.asyncio
async def test_complete_task(tasks_api):
    respx.post("http://localhost:8080/v2/user-tasks/555/completion").mock(
        return_value=httpx.Response(204)
    )
    await tasks_api.complete(task_key="555", variables={"approved": True})


@respx.mock
@pytest.mark.asyncio
async def test_assign_task(tasks_api):
    respx.patch("http://localhost:8080/v2/user-tasks/555/assign").mock(
        return_value=httpx.Response(204)
    )
    await tasks_api.assign(task_key="555", assignee="bob")
