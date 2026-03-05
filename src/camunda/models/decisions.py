"""Decision (DMN) models."""

from __future__ import annotations

from typing import Any

from camunda.models.common import CamundaModel


class DecisionEvaluationResult(CamundaModel):
    """Result of evaluating a DMN decision."""

    decision_definition_key: str
    decision_definition_id: str
    decision_definition_version: int
    decision_requirements_key: str | None = None
    decision_requirements_id: str | None = None
    output: str
    evaluated_decisions: list[dict[str, Any]] = []
    tenant_id: str | None = None
