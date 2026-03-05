"""LangChain Tool implementations for Camunda operations."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool
from pydantic import Field


class StartProcessTool(BaseTool):
    """Start a Camunda BPMN process instance."""

    name: str = "camunda_start_process"
    description: str = (
        "Start a new BPMN process instance in Camunda. "
        "Provide the process_definition_id and variables as a JSON string."
    )
    client: Any = Field(exclude=True)

    async def _arun(
        self,
        process_definition_id: str,
        variables: str = "{}",
    ) -> str:
        vars_dict = json.loads(variables) if isinstance(variables, str) else variables
        result = await self.client.processes.start(
            process_definition_id=process_definition_id,
            variables=vars_dict,
        )
        return (
            f"Started process '{result.process_definition_id}' "
            f"with instance key {result.process_instance_key}"
        )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use async: await tool.arun()")


class CompleteTaskTool(BaseTool):
    """Complete a Camunda user task."""

    name: str = "camunda_complete_task"
    description: str = (
        "Complete a user task in Camunda. "
        "Provide the task_key and variables as a JSON string."
    )
    client: Any = Field(exclude=True)

    async def _arun(self, task_key: str, variables: str = "{}") -> str:
        vars_dict = json.loads(variables) if isinstance(variables, str) else variables
        await self.client.tasks.complete(task_key=task_key, variables=vars_dict)
        return f"Completed task {task_key}"

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use async: await tool.arun()")


class SendMessageTool(BaseTool):
    """Publish a message to Camunda for correlation."""

    name: str = "camunda_send_message"
    description: str = (
        "Send a message to Camunda for correlation with a waiting process. "
        "Provide message name, correlation_key, and variables as JSON string."
    )
    client: Any = Field(exclude=True)

    async def _arun(
        self,
        name: str,
        correlation_key: str,
        variables: str = "{}",
    ) -> str:
        vars_dict = json.loads(variables) if isinstance(variables, str) else variables
        result = await self.client.messages.publish(
            name=name,
            correlation_key=correlation_key,
            variables=vars_dict,
        )
        return f"Published message '{name}' with key {result.message_key}"

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use async: await tool.arun()")


class EvaluateDecisionTool(BaseTool):
    """Evaluate a Camunda DMN decision table."""

    name: str = "camunda_evaluate_decision"
    description: str = (
        "Evaluate a DMN decision table in Camunda. "
        "Provide decision_definition_id and variables as JSON string."
    )
    client: Any = Field(exclude=True)

    async def _arun(
        self,
        decision_definition_id: str,
        variables: str = "{}",
    ) -> str:
        vars_dict = json.loads(variables) if isinstance(variables, str) else variables
        result = await self.client.decisions.evaluate(
            decision_definition_id=decision_definition_id,
            variables=vars_dict,
        )
        return f"Decision '{result.decision_definition_id}' output: {result.output}"

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use async: await tool.arun()")


class SearchProcessInstancesTool(BaseTool):
    """Search for Camunda process instances."""

    name: str = "camunda_search_processes"
    description: str = (
        "Search for process instances in Camunda. "
        'Provide a filter as a JSON string (e.g., {"state": "ACTIVE"}).'
    )
    client: Any = Field(exclude=True)

    async def _arun(self, filter: str = "{}") -> str:
        filter_dict = json.loads(filter) if isinstance(filter, str) else filter
        result = await self.client.processes.search(filter=filter_dict)
        instances = [
            f"  - {pi.process_definition_id} (key={pi.process_instance_key}, state={pi.state})"
            for pi in result.items
        ]
        return f"Found {len(result.items)} instances:\n" + "\n".join(instances)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("Use async: await tool.arun()")
