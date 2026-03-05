"""Basic job worker — process documents with an ML model."""

import asyncio

from camunda import CamundaClient
from camunda.auth import BasicAuth
from camunda.models import Job


async def main():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )

    @client.job_worker("classify-document", timeout_ms=30000)
    async def classify(job: Job) -> dict:
        url = job.variables.get("document_url", "")
        print(f"Classifying document: {url}")
        # Your ML model here
        return {"classification": "invoice", "confidence": 0.95}

    print("Starting worker... (Ctrl+C to stop)")
    try:
        await client.run_workers()
    except KeyboardInterrupt:
        client.stop_workers()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
