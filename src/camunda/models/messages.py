"""Message models."""

from __future__ import annotations

from camunda.models.common import CamundaModel


class MessagePublicationResult(CamundaModel):
    """Result of publishing a message."""

    message_key: str
    tenant_id: str | None = None


class MessageCorrelationResult(CamundaModel):
    """Result of correlating a message."""

    process_instance_key: str
    tenant_id: str | None = None
