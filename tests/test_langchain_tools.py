import httpx
import pytest
import respx

from camunda import CamundaClient
from camunda.auth.base import NoAuth


@pytest.fixture
def client():
    return CamundaClient(base_url="http://localhost:8080", auth=NoAuth())


def test_toolkit_returns_tools(client):
    from camunda.langchain.toolkit import CamundaToolkit

    toolkit = CamundaToolkit(client=client)
    tools = toolkit.get_tools()
    assert len(tools) >= 4
    tool_names = [t.name for t in tools]
    assert "camunda_start_process" in tool_names
    assert "camunda_complete_task" in tool_names
    assert "camunda_send_message" in tool_names
    assert "camunda_evaluate_decision" in tool_names


@respx.mock
@pytest.mark.asyncio
async def test_start_process_tool(client):
    from camunda.langchain.tools import StartProcessTool

    respx.post("http://localhost:8080/v2/process-instances").mock(
        return_value=httpx.Response(200, json={
            "processDefinitionKey": "1",
            "processDefinitionId": "test",
            "processDefinitionVersion": 1,
            "processInstanceKey": "99",
            "tenantId": "<default>",
        })
    )
    tool = StartProcessTool(client=client)
    result = await tool._arun(process_definition_id="test", variables="{}")
    assert "99" in result


@respx.mock
@pytest.mark.asyncio
async def test_evaluate_decision_tool(client):
    from camunda.langchain.tools import EvaluateDecisionTool

    respx.post("http://localhost:8080/v2/decision-definitions/evaluation").mock(
        return_value=httpx.Response(200, json={
            "decisionDefinitionKey": "300",
            "decisionDefinitionId": "risk-check",
            "decisionDefinitionVersion": 1,
            "output": '"low"',
            "evaluatedDecisions": [],
            "tenantId": "<default>",
        })
    )
    tool = EvaluateDecisionTool(client=client)
    result = await tool._arun(
        decision_definition_id="risk-check",
        variables='{"credit_score": 720}',
    )
    assert "low" in result
