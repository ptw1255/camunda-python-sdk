import httpx
import pytest
import respx

from camunda._http import HttpClient
from camunda.auth.base import NoAuth
from camunda.config import CamundaConfig
from camunda.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


@pytest.fixture
def config():
    return CamundaConfig(base_url="http://localhost:8080", retry_count=0)


@pytest.fixture
def http_client(config):
    return HttpClient(config=config, auth=NoAuth())


@respx.mock
@pytest.mark.asyncio
async def test_get_request(http_client):
    respx.get("http://localhost:8080/v2/topology").mock(
        return_value=httpx.Response(200, json={"clusterSize": 1})
    )
    result = await http_client.get("/v2/topology")
    assert result == {"clusterSize": 1}


@respx.mock
@pytest.mark.asyncio
async def test_post_request(http_client):
    respx.post("http://localhost:8080/v2/process-instances").mock(
        return_value=httpx.Response(
            200, json={"processInstanceKey": "123", "processDefinitionId": "test"}
        )
    )
    result = await http_client.post(
        "/v2/process-instances",
        json={"processDefinitionId": "test", "variables": {}},
    )
    assert result["processInstanceKey"] == "123"


@respx.mock
@pytest.mark.asyncio
async def test_404_raises_not_found(http_client):
    respx.get("http://localhost:8080/v2/process-instances/999").mock(
        return_value=httpx.Response(404, json={"message": "Not found"})
    )
    with pytest.raises(NotFoundError) as exc_info:
        await http_client.get("/v2/process-instances/999")
    assert exc_info.value.status_code == 404


@respx.mock
@pytest.mark.asyncio
async def test_401_raises_auth_error(http_client):
    respx.get("http://localhost:8080/v2/topology").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )
    with pytest.raises(AuthenticationError):
        await http_client.get("/v2/topology")


@respx.mock
@pytest.mark.asyncio
async def test_409_raises_conflict(http_client):
    respx.post("http://localhost:8080/v2/user-tasks/1/completion").mock(
        return_value=httpx.Response(409, json={"message": "Already completed"})
    )
    with pytest.raises(ConflictError):
        await http_client.post("/v2/user-tasks/1/completion", json={})


@respx.mock
@pytest.mark.asyncio
async def test_429_raises_rate_limit(http_client):
    respx.get("http://localhost:8080/v2/topology").mock(
        return_value=httpx.Response(429, json={"message": "Too many requests"})
    )
    with pytest.raises(RateLimitError):
        await http_client.get("/v2/topology")


@respx.mock
@pytest.mark.asyncio
async def test_500_raises_server_error(http_client):
    respx.get("http://localhost:8080/v2/topology").mock(
        return_value=httpx.Response(500, json={"message": "Internal error"})
    )
    with pytest.raises(ServerError):
        await http_client.get("/v2/topology")


@respx.mock
@pytest.mark.asyncio
async def test_204_returns_none(http_client):
    respx.post("http://localhost:8080/v2/jobs/1/completion").mock(
        return_value=httpx.Response(204)
    )
    result = await http_client.post("/v2/jobs/1/completion", json={})
    assert result is None
