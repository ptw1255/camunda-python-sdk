
import httpx
import pytest
import respx

from camunda.auth.basic import BasicAuth
from camunda.auth.bearer import BearerToken
from camunda.auth.cookie import CookieAuth
from camunda.auth.oauth import OAuthCredentials


def test_basic_auth_applies_header():
    auth = BasicAuth(username="demo", password="demo")
    request = httpx.Request("GET", "http://localhost:8080/v2/topology")
    flow = auth.auth_flow(request)
    modified = next(flow)
    assert modified.headers["authorization"].startswith("Basic ")


def test_bearer_auth_applies_header():
    auth = BearerToken(token="my-jwt-token")
    request = httpx.Request("GET", "http://localhost:8080/v2/topology")
    flow = auth.auth_flow(request)
    modified = next(flow)
    assert modified.headers["authorization"] == "Bearer my-jwt-token"


@respx.mock
@pytest.mark.asyncio
async def test_oauth_fetches_and_caches_token():
    respx.post("https://login.cloud.camunda.io/oauth/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "test-token-123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
    )
    auth = OAuthCredentials(
        client_id="test-id",
        client_secret="test-secret",
        token_url="https://login.cloud.camunda.io/oauth/token",
        audience="zeebe.camunda.io",
    )
    token = await auth.get_token()
    assert token == "test-token-123"

    token2 = await auth.get_token()
    assert token2 == "test-token-123"
    assert respx.calls.call_count == 1


def test_cookie_auth_applies_header():
    auth = CookieAuth(cookie_name="SESSION", cookie_value="abc123")
    request = httpx.Request("GET", "http://localhost:8080/v2/topology")
    flow = auth.auth_flow(request)
    modified = next(flow)
    assert "SESSION=abc123" in modified.headers.get("cookie", "")
