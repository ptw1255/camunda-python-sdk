from camunda.models.common import SearchResult
from camunda.models.processes import ProcessInstance, CreateProcessInstanceRequest
from camunda.models.jobs import Job
from camunda.models.tasks import UserTask
from camunda.models.decisions import DecisionEvaluationResult
from camunda.models.incidents import Incident


def test_process_instance_from_api_response():
    data = {
        "processDefinitionKey": "2251799813685249",
        "processDefinitionId": "order-process",
        "processDefinitionVersion": 1,
        "processInstanceKey": "2251799813685251",
        "tenantId": "<default>",
    }
    pi = ProcessInstance.model_validate(data)
    assert pi.process_instance_key == "2251799813685251"
    assert pi.process_definition_id == "order-process"
    assert pi.process_definition_version == 1


def test_create_process_instance_request():
    req = CreateProcessInstanceRequest(
        process_definition_id="order-process",
        variables={"amount": 100},
    )
    payload = req.to_api_dict()
    assert payload["processDefinitionId"] == "order-process"
    assert payload["variables"] == {"amount": 100}
    assert "awaitCompletion" not in payload or payload.get("awaitCompletion") is not True or "awaitCompletion" not in payload


def test_job_from_api_response():
    data = {
        "jobKey": "123",
        "type": "payment-service",
        "processInstanceKey": "456",
        "processDefinitionKey": "789",
        "processDefinitionId": "order-process",
        "processDefinitionVersion": 1,
        "elementId": "Activity_Payment",
        "elementInstanceKey": "012",
        "worker": "worker-1",
        "retries": 3,
        "deadline": 1700000000000,
        "variables": {"orderId": "1234"},
        "tenantId": "<default>",
    }
    job = Job.model_validate(data)
    assert job.job_key == "123"
    assert job.type == "payment-service"
    assert job.variables == {"orderId": "1234"}
    assert job.retries == 3


def test_user_task_from_api_response():
    data = {
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
    }
    task = UserTask.model_validate(data)
    assert task.user_task_key == "555"
    assert task.assignee == "jane"
    assert task.state == "CREATED"


def test_search_result_generic():
    result = SearchResult[ProcessInstance].model_validate({
        "items": [
            {
                "processDefinitionKey": "1",
                "processDefinitionId": "test",
                "processDefinitionVersion": 1,
                "processInstanceKey": "2",
                "tenantId": "<default>",
            }
        ],
        "page": {"totalItems": 1},
    })
    assert len(result.items) == 1
    assert isinstance(result.items[0], ProcessInstance)
    assert result.page.total_items == 1


def test_decision_evaluation_result():
    data = {
        "decisionDefinitionKey": "300",
        "decisionDefinitionId": "risk-check",
        "decisionDefinitionVersion": 1,
        "decisionRequirementsKey": "299",
        "decisionRequirementsId": "risk-drd",
        "output": '"low"',
        "evaluatedDecisions": [],
        "tenantId": "<default>",
    }
    result = DecisionEvaluationResult.model_validate(data)
    assert result.decision_definition_id == "risk-check"
    assert result.output == '"low"'


def test_incident_from_api_response():
    data = {
        "incidentKey": "777",
        "type": "JOB_NO_RETRIES",
        "state": "ACTIVE",
        "processInstanceKey": "456",
        "processDefinitionKey": "789",
        "processDefinitionId": "order-process",
        "elementId": "Activity_Payment",
        "elementInstanceKey": "012",
        "errorMessage": "Connection refused",
        "creationTime": "2026-03-04T12:00:00Z",
        "tenantId": "<default>",
    }
    incident = Incident.model_validate(data)
    assert incident.incident_key == "777"
    assert incident.type == "JOB_NO_RETRIES"
    assert incident.state == "ACTIVE"
