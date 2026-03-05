"""Incident models."""

from __future__ import annotations

from camunda.models.common import CamundaModel


class Incident(CamundaModel):
    """A process incident."""

    incident_key: str
    type: str
    state: str
    process_instance_key: str | None = None
    process_definition_key: str | None = None
    process_definition_id: str | None = None
    element_id: str | None = None
    element_instance_key: str | None = None
    error_message: str | None = None
    creation_time: str | None = None
    tenant_id: str | None = None
