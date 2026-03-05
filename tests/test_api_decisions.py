import httpx
import pytest
import respx

from camunda._http import HttpClient
from camunda.api.decisions import DecisionsApi
from camunda.auth.base import NoAuth
from camunda.config import CamundaConfig


@pytest.fixture
def http_client():
    config = CamundaConfig(base_url="http://localhost:8080", retry_count=0)
    return HttpClient(config=config, auth=NoAuth())


@pytest.fixture
def decisions_api(http_client):
    return DecisionsApi(http_client)


@respx.mock
@pytest.mark.asyncio
async def test_evaluate_decision(decisions_api):
    respx.post("http://localhost:8080/v2/decision-definitions/evaluation").mock(
        return_value=httpx.Response(200, json={
            "decisionDefinitionKey": "300",
            "decisionDefinitionId": "risk-check",
            "decisionDefinitionVersion": 1,
            "decisionRequirementsKey": "299",
            "decisionRequirementsId": "risk-drd",
            "output": '"low"',
            "evaluatedDecisions": [],
            "tenantId": "<default>",
        })
    )
    result = await decisions_api.evaluate(
        decision_definition_id="risk-check",
        variables={"credit_score": 720},
    )
    assert result.decision_definition_id == "risk-check"
    assert result.output == '"low"'
