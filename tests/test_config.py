from camunda.config import CamundaConfig


def test_config_defaults():
    config = CamundaConfig(base_url="http://localhost:8080")
    assert config.base_url == "http://localhost:8080"
    assert config.request_timeout == 30.0
    assert config.retry_count == 3
    assert config.worker_max_jobs == 32
    assert config.tenant_id is None


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("CAMUNDA_BASE_URL", "https://test.camunda.io")
    monkeypatch.setenv("CAMUNDA_WORKER_MAX_JOBS", "64")
    config = CamundaConfig.from_env()
    assert config.base_url == "https://test.camunda.io"
    assert config.worker_max_jobs == 64


def test_config_from_env_with_overrides(monkeypatch):
    monkeypatch.setenv("CAMUNDA_BASE_URL", "https://env.camunda.io")
    config = CamundaConfig.from_env(base_url="https://override.camunda.io")
    assert config.base_url == "https://env.camunda.io"
