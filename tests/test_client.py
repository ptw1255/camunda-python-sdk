
from camunda import CamundaClient
from camunda.api.processes import ProcessesApi
from camunda.api.tasks import TasksApi
from camunda.api.jobs import JobsApi
from camunda.auth.basic import BasicAuth


def test_client_initializes_sub_clients():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )
    assert isinstance(client.processes, ProcessesApi)
    assert isinstance(client.tasks, TasksApi)
    assert isinstance(client.jobs, JobsApi)


def test_client_from_env(monkeypatch):
    monkeypatch.setenv("CAMUNDA_BASE_URL", "http://localhost:8080")
    monkeypatch.setenv("CAMUNDA_AUTH_TYPE", "basic")
    monkeypatch.setenv("CAMUNDA_USERNAME", "demo")
    monkeypatch.setenv("CAMUNDA_PASSWORD", "demo")
    client = CamundaClient.from_env()
    assert isinstance(client.processes, ProcessesApi)
