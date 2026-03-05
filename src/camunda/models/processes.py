"""Process definition and instance models."""

from __future__ import annotations

from typing import Any

from camunda.models.common import CamundaModel


class ProcessInstance(CamundaModel):
    """A running or completed process instance."""

    process_definition_key: str
    process_definition_id: str
    process_definition_version: int
    process_instance_key: str
    tenant_id: str | None = None
    state: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ProcessDefinition(CamundaModel):
    """A deployed process definition."""

    process_definition_key: str
    process_definition_id: str
    process_definition_version: int
    name: str | None = None
    resource_name: str | None = None
    tenant_id: str | None = None


class CreateProcessInstanceRequest(CamundaModel):
    """Request to start a new process instance."""

    process_definition_id: str | None = None
    process_definition_key: str | None = None
    process_definition_version: int | None = None
    variables: dict[str, Any] = {}
    tenant_id: str | None = None
    await_completion: bool = False

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to API request payload."""
        d: dict[str, Any] = {}
        if self.process_definition_id:
            d["processDefinitionId"] = self.process_definition_id
        if self.process_definition_key:
            d["processDefinitionKey"] = self.process_definition_key
        if self.process_definition_version is not None:
            d["processDefinitionVersion"] = self.process_definition_version
        if self.variables:
            d["variables"] = self.variables
        if self.tenant_id:
            d["tenantId"] = self.tenant_id
        if self.await_completion:
            d["awaitCompletion"] = True
        return d
