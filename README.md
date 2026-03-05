# Camunda Python SDK

**The missing Python SDK for Camunda 8+ — purpose-built for AI/ML engineers building agentic workflows.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Tests: 35 passing](https://img.shields.io/badge/tests-35%20passing-brightgreen.svg)]()

---

## The Problem

Camunda 8 is positioning itself as the **agentic orchestration platform** — the governance and visibility layer that AI agents need to operate in production. But there's a critical gap:

| SDK | Coverage | Maturity |
|-----|----------|----------|
| **Java** (Spring Zeebe) | Full platform | Production-grade, first-class |
| **Node.js/TypeScript** | Full platform | Production-grade, official |
| **Python** (pyzeebe) | ~20% — gRPC job workers only | Community-maintained |

**The irony:** Python is the dominant language for AI/ML development. LangGraph, CrewAI, AutoGen, OpenAI Agents SDK — all Python-first. Camunda's agentic AI story can't succeed if Python developers can't access 80% of the platform.

### What's missing in pyzeebe

| Capability | pyzeebe | This SDK |
|-----------|---------|----------|
| Zeebe gRPC job workers | Yes | Yes (via REST) |
| Unified REST API (8.7+) | No | **Yes** |
| User task management | No | **Yes** |
| DMN decision evaluation | No | **Yes** |
| Process instance queries | No | **Yes** |
| Incident management | No | **Yes** |
| Message correlation | Basic | **Full** |
| Signal broadcasting | No | **Yes** |
| Variable search/update | No | **Yes** |
| Multi-auth (OAuth, Basic, etc.) | Basic | **5 strategies** |
| Pydantic models / IDE support | No | **Full** |
| LangChain integration | No | **Yes** |

This SDK closes the gap from ~20% to ~95% API coverage.

---

## Installation

```bash
pip install camunda-python-sdk                    # Core SDK
pip install camunda-python-sdk[langchain]         # + LangChain/LangGraph tools
```

**Requirements:** Python 3.10+, Camunda 8.7+ (unified REST API)

---

## Quick Start

```python
import asyncio
from camunda import CamundaClient
from camunda.auth import BasicAuth

async def main():
    client = CamundaClient(
        base_url="http://localhost:8080",
        auth=BasicAuth(username="demo", password="demo"),
    )

    # Start a process instance
    instance = await client.processes.start(
        process_definition_id="order-process",
        variables={"amount": 99.95, "customer": "Jane"},
    )
    print(f"Started: {instance.process_instance_key}")

    await client.close()

asyncio.run(main())
```

---

## Key Concepts

### Architecture: Unified REST API Client

This SDK is built entirely on Camunda's **unified Orchestration Cluster REST API** (introduced in 8.7, GA in 8.8). This is a deliberate design choice:

- **Future-proof** — Camunda is deprecating the separate component APIs (Zeebe, Operate, Tasklist) in 8.10 in favor of the unified API
- **Single transport** — HTTP only, no protobuf/gRPC compilation required
- **Firewall-friendly** — Works through proxies and corporate firewalls
- **Simple auth** — Standard HTTP auth headers, no gRPC channel credentials

All endpoints use the `/v2/` path prefix and return JSON.

### Async-First Design

Every API call is `async`. This is intentional — AI/ML workloads are I/O-bound (waiting for LLM inference, database queries, external APIs). Async lets you run multiple workers and API calls concurrently:

```python
import asyncio

# Run multiple operations concurrently
results = await asyncio.gather(
    client.processes.search(filter={"state": "ACTIVE"}),
    client.tasks.search(filter={"assignee": "ai-agent"}),
    client.incidents.search(filter={"state": "ACTIVE"}),
)
```

### Pydantic Models

All API responses are **Pydantic v2 models** with full IDE autocomplete. No more guessing dictionary keys:

```python
instance = await client.processes.start(process_definition_id="order-process")
instance.process_instance_key   # str — IDE knows the type
instance.process_definition_id  # str
instance.process_definition_version  # int

# Search results are generic
results: SearchResult[UserTask] = await client.tasks.search(filter={...})
for task in results.items:       # list[UserTask] — fully typed
    task.user_task_key           # str
    task.assignee                # str | None
    task.creation_date           # str | None
```

The models handle **camelCase ↔ snake_case** conversion automatically. The Camunda API returns `processInstanceKey`, your Python code uses `process_instance_key`.

### The Client Object

Everything hangs off a single `CamundaClient`:

```python
client = CamundaClient(base_url="...", auth=BasicAuth(...))

client.processes       # Start, cancel, search process instances
client.jobs            # Activate, complete, fail jobs
client.tasks           # User task lifecycle (search, assign, complete)
client.decisions       # Evaluate DMN decision tables
client.messages        # Publish and correlate messages
client.signals         # Broadcast signals
client.incidents       # Query and resolve incidents
client.variables       # Search and inspect variables
client.deployments     # Deploy BPMN/DMN/forms
client.topology        # Cluster topology info
```

---

## Authentication

Five strategies matching the Node.js SDK:

### SaaS (OAuth2 — recommended for production)

```python
from camunda.auth import OAuthCredentials

client = CamundaClient(
    base_url="https://bru-2.camunda.io/YOUR-CLUSTER-ID",
    auth=OAuthCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
        # token_url and audience auto-detected for SaaS
    ),
)
```

OAuth tokens are **automatically cached and refreshed** before expiry. No manual token management needed.

### Self-Managed (Basic Auth)

```python
from camunda.auth import BasicAuth

client = CamundaClient(
    base_url="http://localhost:8080",
    auth=BasicAuth(username="demo", password="demo"),
)
```

### Environment Variables (Zero-Config)

```python
# Set these environment variables:
#   CAMUNDA_BASE_URL=http://localhost:8080
#   CAMUNDA_AUTH_TYPE=basic  (or: oauth, bearer, none)
#   CAMUNDA_USERNAME=demo
#   CAMUNDA_PASSWORD=demo

client = CamundaClient.from_env()
```

### All Auth Options

| Strategy | Use Case |
|----------|----------|
| `OAuthCredentials(client_id, client_secret)` | SaaS + self-managed OAuth |
| `BasicAuth(username, password)` | Self-managed basic auth |
| `BearerToken(token)` | Pre-obtained JWT tokens |
| `CookieAuth(cookie_name, cookie_value)` | Session-based auth |
| `NoAuth()` | mTLS or local dev environments |

---

## Use Case 1: Job Workers (Service Task Execution)

Job workers are the core programming model in Camunda 8. When a process reaches a service task, the engine creates a "job." Your worker picks it up, runs business logic, and reports the result.

**This is how you connect ML models, AI inference, and any Python code to BPMN processes.**

```python
from camunda import CamundaClient
from camunda.auth import BasicAuth
from camunda.models import Job

client = CamundaClient(
    base_url="http://localhost:8080",
    auth=BasicAuth(username="demo", password="demo"),
)

@client.job_worker("classify-document", timeout_ms=30000)
async def classify_document(job: Job) -> dict:
    """Called when the engine reaches a 'classify-document' service task."""
    document_url = job.variables["document_url"]

    # Run your ML model
    result = await my_classifier.predict(document_url)

    # Return variables to the process
    return {
        "classification": result.label,
        "confidence": result.score,
        "model_version": "v2.1",
    }

@client.job_worker("send-notification", timeout_ms=10000)
async def send_notification(job: Job) -> dict:
    """Multiple workers can run concurrently."""
    await email_service.send(
        to=job.variables["customer_email"],
        template="order-confirmation",
    )
    return {"notification_sent": True}

# Start all workers — blocks until stop_workers() is called
import asyncio
asyncio.run(client.run_workers())
```

**How it works under the hood:**
1. The SDK polls `POST /v2/jobs/activation` at a configurable interval
2. For each activated job, it calls your handler function
3. If the handler returns a dict, the SDK calls `POST /v2/jobs/{key}/completion` with those variables
4. If the handler raises an exception, the SDK calls `POST /v2/jobs/{key}/failure` with decremented retries

---

## Use Case 2: Human-in-the-Loop (User Tasks)

The #1 missing capability in pyzeebe. **User tasks are how you add human oversight to AI workflows** — the human-in-the-loop pattern that every production AI system needs.

### The Pattern

```
[AI classifies document] → [Human reviews classification] → [Process continues]
         ↑ job worker              ↑ user task
```

### Starting a Process with Human Review

```python
# Start a process that includes both AI and human tasks
instance = await client.processes.start(
    process_definition_id="ai-document-review",
    variables={
        "document_url": "https://example.com/contract.pdf",
        "ai_classification": "high-risk",
        "confidence": 0.73,  # Below threshold — needs human review
    },
)
```

### Querying and Completing User Tasks

```python
# Find tasks assigned to the AI review team
tasks = await client.tasks.search(
    filter={
        "state": "CREATED",
        "candidateGroups": ["ai-reviewers"],
        "processDefinitionId": "ai-document-review",
    }
)

for task in tasks.items:
    print(f"Task: {task.element_id}")
    print(f"Assigned to: {task.assignee}")
    print(f"Created: {task.creation_date}")

    # A human (or a more capable AI) reviews and completes the task
    await client.tasks.complete(
        task_key=task.user_task_key,
        variables={
            "approved": True,
            "reviewer_notes": "Classification is correct, proceed.",
            "reviewed_by": "jane.doe",
        },
    )
```

### Task Assignment

```python
# Assign a task to a specific person
await client.tasks.assign(task_key="12345", assignee="jane.doe")

# Unassign (return to the pool)
await client.tasks.unassign(task_key="12345")
```

---

## Use Case 3: DMN Guardrails (Business Rules for AI)

DMN (Decision Model and Notation) tables are **business rules that constrain what AI agents can do**. Instead of hardcoding rules in Python, you define them in a visual decision table that business stakeholders can review and modify.

### Why This Matters for AI

- **Compliance**: Regulated industries require auditable decision logic
- **Separation of concerns**: Business rules change independently of AI model code
- **Safety**: Prevent AI from making decisions outside approved boundaries
- **Transparency**: Non-technical stakeholders can read DMN tables

### Evaluating a Decision

```python
# Before the AI agent approves a loan, check business rules
result = await client.decisions.evaluate(
    decision_definition_id="loan-eligibility",
    variables={
        "credit_score": 720,
        "loan_amount": 50000,
        "employment_years": 3,
        "debt_to_income_ratio": 0.28,
    },
)

print(result.output)  # '"approved"' or '"denied"' or '"manual_review"'
print(result.decision_definition_id)  # "loan-eligibility"

# Use the DMN output to gate AI behavior
import json
decision = json.loads(result.output)
if decision == "approved":
    # AI agent can proceed autonomously
    await client.messages.publish(
        name="loan-approved",
        correlation_key=application_id,
        variables={"approved_amount": 50000},
    )
elif decision == "manual_review":
    # Route to human reviewer
    print("DMN says manual review required — escalating")
else:
    # Denied — AI must not proceed
    print("DMN denied the application — blocking AI agent")
```

---

## Use Case 4: Message Correlation (Agent-to-Agent Communication)

Messages are how **different parts of a process communicate asynchronously**. In agentic workflows, this enables:

- **Agent-to-agent coordination**: One agent publishes a result, another agent's process catches it
- **Event-driven workflows**: External events (webhooks, Kafka messages) trigger process advancement
- **Parallel coordination**: Multiple agents work independently, messages synchronize them

### Publishing a Message

```python
# Agent A finishes document classification — notify the waiting process
await client.messages.publish(
    name="document-classified",           # Must match the BPMN catch event name
    correlation_key=order_id,             # Routes to the right process instance
    variables={
        "classification": "invoice",
        "confidence": 0.97,
        "extracted_fields": {"vendor": "Acme", "amount": 1500.00},
    },
    time_to_live=300_000,                 # Buffer for 5 minutes if no subscriber yet
)
```

### Correlating a Message (Synchronous)

```python
# Publish AND immediately correlate — returns the matched process instance
result = await client.messages.correlate(
    name="payment-received",
    correlation_key=invoice_id,
    variables={"payment_method": "wire", "amount": 1500.00},
)
print(f"Correlated to process: {result.process_instance_key}")
```

### Signal Broadcasting (Fan-Out)

```python
# Broadcast to ALL processes with a matching signal catch event
await client.signals.broadcast(
    signal_name="system-maintenance-mode",
    variables={"maintenance_window": "2h", "priority": "high"},
)
```

---

## Use Case 5: LangChain/LangGraph Integration

The optional `[langchain]` extras turn Camunda into a **set of tools that any LangChain agent can call**. This is the bridge between the AI framework world and the process orchestration world.

### Installation

```bash
pip install camunda-python-sdk[langchain]
```

### The Toolkit

```python
from camunda import CamundaClient
from camunda.auth import BasicAuth
from camunda.langchain import CamundaToolkit

client = CamundaClient(
    base_url="http://localhost:8080",
    auth=BasicAuth(username="demo", password="demo"),
)

toolkit = CamundaToolkit(client=client)
tools = toolkit.get_tools()
```

This gives your agent 5 tools:

| Tool | What it does |
|------|-------------|
| `camunda_start_process` | Start a BPMN process instance with variables |
| `camunda_complete_task` | Complete a user task (human-in-the-loop approval) |
| `camunda_send_message` | Publish a message for correlation |
| `camunda_evaluate_decision` | Evaluate a DMN decision table |
| `camunda_search_processes` | Query running process instances |

### Using with a LangChain Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a loan processing agent. Use Camunda tools to manage loan applications."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = await executor.ainvoke({
    "input": "Start a loan approval process for Jane Doe requesting $75,000, "
             "then check if she's eligible using the credit-rating decision table "
             "with a credit score of 720."
})
```

The agent will:
1. Call `camunda_start_process` to create the loan-approval process instance
2. Call `camunda_evaluate_decision` to check the credit-rating DMN table
3. Reason about the results and take appropriate action

### Using Individual Tools

```python
from camunda.langchain import StartProcessTool, EvaluateDecisionTool

# Use tools directly without a full agent
start_tool = StartProcessTool(client=client)
result = await start_tool.ainvoke({
    "process_definition_id": "loan-approval",
    "variables": '{"applicant": "Jane Doe", "amount": 75000}',
})
print(result)  # "Started process 'loan-approval' with instance key 2251799813685251"
```

---

## Use Case 6: Process Monitoring & Incident Recovery

Production AI workflows fail. Models return unexpected results, APIs timeout, data is malformed. Camunda tracks all of this as **incidents** — and this SDK lets you build automated recovery.

### Querying Process Instances

```python
# Find all active processes of a specific type
active = await client.processes.search(
    filter={
        "processDefinitionId": "ai-document-pipeline",
        "state": "ACTIVE",
    },
    limit=100,
)
print(f"{len(active.items)} active pipeline instances")

# Get details of a specific instance
instance = await client.processes.get("2251799813685251")
```

### Incident Detection and Resolution

```python
# Find all active incidents
incidents = await client.incidents.search(
    filter={"state": "ACTIVE", "type": "JOB_NO_RETRIES"}
)

for incident in incidents.items:
    print(f"Incident {incident.incident_key}: {incident.error_message}")
    print(f"  Process: {incident.process_definition_id}")
    print(f"  Element: {incident.element_id}")

    # Auto-resolve after fixing the root cause
    await client.incidents.resolve(incident.incident_key)
```

### Variable Inspection

```python
# Check what variables a process instance has
variables = await client.variables.search(
    filter={"processInstanceKey": "2251799813685251"}
)
for var in variables.items:
    print(f"  {var.name} = {var.value}")
```

---

## Use Case 7: BPMN/DMN Deployment

Deploy process definitions and decision tables programmatically — useful for CI/CD pipelines.

```python
# Deploy a BPMN process and DMN decision table
result = await client.deployments.deploy(
    "processes/loan-approval.bpmn",
    "decisions/credit-rating.dmn",
)
print(f"Deployment key: {result.deployment_key}")
for deployment in result.deployments:
    print(f"  Deployed: {deployment}")
```

---

## Error Handling

All API errors are mapped to typed exceptions:

```python
from camunda.exceptions import (
    CamundaError,          # Base — catch all Camunda errors
    AuthenticationError,   # 401/403 — bad credentials or permissions
    NotFoundError,         # 404 — process/task/resource not found
    ConflictError,         # 409 — task already completed, etc.
    RateLimitError,        # 429 — too many requests
    ServerError,           # 5xx — server-side failure
    JobTimeoutError,       # Job worker specific
)

try:
    await client.tasks.complete(task_key="12345", variables={"approved": True})
except NotFoundError as e:
    print(f"Task not found: {e.detail}")
    print(f"Status: {e.status_code}")  # 404
except ConflictError as e:
    print(f"Task already completed: {e.detail}")
except CamundaError as e:
    print(f"Unexpected error: {e}")
```

**Automatic retries:** The HTTP client retries on transient failures (connection errors, timeouts, 5xx) with exponential backoff. Configurable via `retry_count` and `retry_backoff`.

---

## Configuration

```python
from camunda import CamundaClient
from camunda.config import CamundaConfig

config = CamundaConfig(
    base_url="http://localhost:8080",
    request_timeout=30.0,        # HTTP timeout in seconds
    retry_count=3,               # Retries on transient failures
    retry_backoff=1.0,           # Exponential backoff base
    worker_poll_interval=0.5,    # Job poll frequency (seconds)
    worker_max_jobs=32,          # Max jobs per poll
    worker_default_timeout_ms=300_000,  # Job lock timeout
    tenant_id=None,              # Multi-tenancy
)

client = CamundaClient(config=config, auth=my_auth)
```

All values can be set via `CAMUNDA_` environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CAMUNDA_BASE_URL` | — | Cluster REST API URL |
| `CAMUNDA_AUTH_TYPE` | `none` | `oauth`, `basic`, `bearer`, or `none` |
| `CAMUNDA_CLIENT_ID` | — | OAuth client ID |
| `CAMUNDA_CLIENT_SECRET` | — | OAuth client secret |
| `CAMUNDA_USERNAME` | — | Basic auth username |
| `CAMUNDA_PASSWORD` | — | Basic auth password |
| `CAMUNDA_TOKEN` | — | Bearer token |
| `CAMUNDA_REQUEST_TIMEOUT` | `30.0` | HTTP timeout (seconds) |
| `CAMUNDA_RETRY_COUNT` | `3` | Retry attempts |
| `CAMUNDA_WORKER_POLL_INTERVAL` | `0.5` | Poll interval (seconds) |
| `CAMUNDA_WORKER_MAX_JOBS` | `32` | Max jobs per activation |

---

## Full API Reference

| Sub-Client | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| `client.processes` | `start()` | `POST /v2/process-instances` | Start a process instance |
| | `get()` | `GET /v2/process-instances/{key}` | Get instance details |
| | `cancel()` | `POST /v2/process-instances/{key}/cancellation` | Cancel an instance |
| | `search()` | `POST /v2/process-instances/search` | Search instances with filters |
| | `get_xml()` | `GET /v2/process-definitions/{key}/xml` | Get BPMN XML |
| `client.jobs` | `activate()` | `POST /v2/jobs/activation` | Activate available jobs |
| | `complete()` | `POST /v2/jobs/{key}/completion` | Complete a job |
| | `fail()` | `POST /v2/jobs/{key}/failure` | Report job failure |
| | `throw_error()` | `POST /v2/jobs/{key}/error` | Throw BPMN error |
| `client.tasks` | `search()` | `POST /v2/user-tasks/search` | Search user tasks |
| | `get()` | `GET /v2/user-tasks/{key}` | Get task details |
| | `complete()` | `POST /v2/user-tasks/{key}/completion` | Complete a task |
| | `assign()` | `PATCH /v2/user-tasks/{key}/assign` | Assign to user |
| | `unassign()` | `PATCH /v2/user-tasks/{key}/unassign` | Unassign |
| `client.decisions` | `evaluate()` | `POST /v2/decision-definitions/evaluation` | Evaluate DMN table |
| `client.messages` | `publish()` | `POST /v2/messages/publication` | Publish message |
| | `correlate()` | `POST /v2/messages/correlation` | Correlate message |
| `client.signals` | `broadcast()` | `POST /v2/signals/broadcast` | Broadcast signal |
| `client.incidents` | `search()` | `POST /v2/incidents/search` | Search incidents |
| | `get()` | `GET /v2/incidents/{key}` | Get incident details |
| | `resolve()` | `POST /v2/incidents/{key}/resolution` | Resolve incident |
| `client.variables` | `search()` | `POST /v2/variables/search` | Search variables |
| | `get()` | `GET /v2/variables/{key}` | Get variable |
| `client.deployments` | `deploy()` | `POST /v2/deployments` | Deploy resources |
| `client.topology` | `get()` | `GET /v2/topology` | Cluster topology |

---

## Examples

The [`examples/`](examples/) directory contains runnable scripts:

| Example | Description |
|---------|-------------|
| [`basic_worker.py`](examples/basic_worker.py) | ML model serving as a Camunda job worker |
| [`human_in_the_loop.py`](examples/human_in_the_loop.py) | AI classification with human review step |
| [`dmn_guardrails.py`](examples/dmn_guardrails.py) | Business rules gating AI agent behavior |
| [`agentic_loan_approval.py`](examples/agentic_loan_approval.py) | LangChain agent using Camunda tools |

---

## Project Structure

```
camunda-python-sdk/
├── src/camunda/
│   ├── __init__.py              # CamundaClient, CamundaConfig exports
│   ├── client.py                # Main client class
│   ├── config.py                # Pydantic configuration model
│   ├── _http.py                 # httpx wrapper with retry/auth/error mapping
│   ├── worker.py                # Job worker decorator + polling loop
│   ├── exceptions.py            # Typed exception hierarchy
│   ├── auth/                    # 5 authentication strategies
│   ├── api/                     # 10 API sub-clients
│   ├── models/                  # Pydantic response/request models
│   ├── langchain/               # Optional LangChain tools + toolkit
│   └── py.typed                 # PEP 561 type checking marker
├── tests/                       # 35 tests with respx HTTP mocking
├── examples/                    # 4 runnable example scripts
└── pyproject.toml               # Modern Python packaging (hatchling)
```

---

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| HTTP | `httpx` (async) | Best Python async HTTP client; used by OpenAI and Anthropic SDKs |
| Models | Pydantic v2 | Industry standard; IDE support; validation |
| Auth | `httpx.Auth` subclasses | Native httpx integration; composable |
| Build | `hatchling` | Modern, fast Python build backend |
| Tests | `pytest` + `pytest-asyncio` + `respx` | Async-native test stack with HTTP mocking |
| Lint | `ruff` | Fast Python linter/formatter |

---

## Contributing

This SDK was built as part of a Camunda GTM analysis project. Contributions welcome — especially:

- Additional API coverage (batch operations, document handling)
- LangGraph node helpers for common patterns
- MCP (Model Context Protocol) server integration
- A2A (Agent-to-Agent) protocol support
- Integration tests against a live Camunda cluster

---

## License

Apache License 2.0
