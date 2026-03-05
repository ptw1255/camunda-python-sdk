"""CamundaToolkit -- all Camunda tools as a LangChain toolkit."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

from camunda.langchain.tools import (
    CompleteTaskTool,
    EvaluateDecisionTool,
    SearchProcessInstancesTool,
    SendMessageTool,
    StartProcessTool,
)


class CamundaToolkit:
    """LangChain toolkit providing Camunda tools to agents."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def get_tools(self) -> list[BaseTool]:
        return [
            StartProcessTool(client=self._client),
            CompleteTaskTool(client=self._client),
            SendMessageTool(client=self._client),
            EvaluateDecisionTool(client=self._client),
            SearchProcessInstancesTool(client=self._client),
        ]
