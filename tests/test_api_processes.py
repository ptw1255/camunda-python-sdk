import httpx
import pytest
import respx

from camunda._http import HttpClient
from camunda.api.processes import ProcessesApi
from camunda.auth.base import NoAuth
from camunda.config import CamundaConfig
from camunda.models import ProcessInstance


@pytest.fixture
def http_client():
    config = CamundaConfig(base_url="http://localhost:8080", retry_count=0)
    return HttpClient(config=config, auth=NoAuth())


@pytest.fixture
def processes_api(http_client):
    return ProcessesApi(http_client)


@respx.mock
@pytest.mark.asyncio
async def test_start_process(processes_api):
    respx.post("http://localhost:8080/v2/process-instances").mock(
        return_value=httpx.Response(200, json={
            "processDefinitionKey": "1",
            "processDefinitionId": "order-process",
            "processDefinitionVersion": 1,
            "processInstanceKey": "2",
            "tenantId": "<default>",
        })
    )
    result = await processes_api.start(
        process_definition_id="order-process",
        variables={"amount": 100},
    )
    assert isinstance(result, ProcessInstance)
    assert result.process_instance_key == "2"


@respx.mock
@pytest.mark.asyncio
async def test_cancel_process(processes_api):
    respx.post("http://localhost:8080/v2/process-instances/2/cancellation").mock(
        return_value=httpx.Response(204)
    )
    await processes_api.cancel(process_instance_key="2")


@respx.mock
@pytest.mark.asyncio
async def test_search_processes(processes_api):
    respx.post("http://localhost:8080/v2/process-instances/search").mock(
        return_value=httpx.Response(200, json={
            "items": [{
                "processDefinitionKey": "1",
                "processDefinitionId": "order-process",
                "processDefinitionVersion": 1,
                "processInstanceKey": "2",
                "tenantId": "<default>",
                "state": "ACTIVE",
            }],
            "page": {"totalItems": 1},
        })
    )
    result = await processes_api.search(filter={"state": "ACTIVE"})
    assert len(result.items) == 1
    assert result.items[0].state == "ACTIVE"
