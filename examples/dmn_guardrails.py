"""DMN guardrails: evaluate business rules before AI acts."""

import asyncio

from camunda import CamundaClient
from camunda.auth import BasicAuth


async def main():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )

    # AI agent wants to approve a loan — check business rules first
    result = await client.decisions.evaluate(
        decision_definition_id="loan-eligibility",
        variables={"credit_score": 720, "loan_amount": 50000, "employment_years": 3},
    )
    print(f"DMN output: {result.output}")

    if '"approved"' in result.output.lower() or '"low"' in result.output.lower():
        print("Business rules approve — AI agent can proceed")
    else:
        print("Business rules reject — escalating to human reviewer")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
