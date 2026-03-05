"""Human-in-the-loop: AI classifies, human reviews."""

import asyncio

from camunda import CamundaClient
from camunda.auth import BasicAuth


async def main():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )

    # Start a process with an AI task followed by human review
    instance = await client.processes.start(
        process_definition_id="ai-document-review",
        variables={"document_url": "https://example.com/doc.pdf"},
    )
    print(f"Started process: {instance.process_instance_key}")

    # Query for human review tasks
    tasks = await client.tasks.search(
        filter={"processDefinitionId": "ai-document-review", "state": "CREATED"}
    )
    for task in tasks.items:
        print(f"Task {task.user_task_key}: {task.element_id} assigned to {task.assignee}")
        await client.tasks.complete(
            task_key=task.user_task_key,
            variables={"approved": True, "reviewer_notes": "Classification looks correct"},
        )
        print(f"Completed task {task.user_task_key}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
