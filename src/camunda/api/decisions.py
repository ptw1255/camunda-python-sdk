"""Decision (DMN) API."""

from __future__ import annotations

from typing import Any

from camunda._http import HttpClient
from camunda.models.decisions import DecisionEvaluationResult


class DecisionsApi:
    """Client for DMN decision operations."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def evaluate(
        self,
        *,
        decision_definition_id: str | None = None,
        decision_definition_key: str | None = None,
        variables: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> DecisionEvaluationResult:
        payload: dict[str, Any] = {}
        if decision_definition_id:
            payload["decisionDefinitionId"] = decision_definition_id
        if decision_definition_key:
            payload["decisionDefinitionKey"] = decision_definition_key
        if variables:
            payload["variables"] = variables
        if tenant_id:
            payload["tenantId"] = tenant_id
        data = await self._http.post("/v2/decision-definitions/evaluation", json=payload)
        return DecisionEvaluationResult.model_validate(data)
