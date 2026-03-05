"""User task models."""

from __future__ import annotations

from camunda.models.common import CamundaModel


class UserTask(CamundaModel):
    """A user task instance."""

    user_task_key: str
    state: str
    assignee: str | None = None
    candidate_groups: list[str] = []
    candidate_users: list[str] = []
    process_instance_key: str | None = None
    process_definition_id: str | None = None
    element_id: str | None = None
    creation_date: str | None = None
    follow_up_date: str | None = None
    due_date: str | None = None
    form_key: str | None = None
    tenant_id: str | None = None
