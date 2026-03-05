"""Agentic loan approval: LangChain agent with Camunda tools."""

import asyncio

from camunda import CamundaClient
from camunda.auth import BasicAuth
from camunda.langchain import CamundaToolkit

# Requires: pip install camunda-sdk[langchain] langchain-openai


async def main():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )

    toolkit = CamundaToolkit(client=client)
    tools = toolkit.get_tools()
    print(f"Available Camunda tools: {[t.name for t in tools]}")

    # Use tools directly (in practice, called by an LLM agent)
    start_tool = tools[0]  # StartProcessTool
    result = await start_tool.ainvoke({
        "process_definition_id": "loan-approval",
        "variables": '{"applicant": "Jane Doe", "amount": 75000}',
    })
    print(result)

    decision_tool = tools[3]  # EvaluateDecisionTool
    result = await decision_tool.ainvoke({
        "decision_definition_id": "credit-rating",
        "variables": '{"credit_score": 720, "loan_amount": 75000}',
    })
    print(result)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
