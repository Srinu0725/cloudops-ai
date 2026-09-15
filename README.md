# CloudOps AI

> **Agentic AI-powered production incident investigation and root-cause analysis platform.**

CloudOps AI is an **Agentic AI system for investigating production incidents automatically**.

Instead of requiring an engineer to manually inspect metrics, logs, recent deployments, and operational documentation, CloudOps AI uses an AI agent to gather evidence through tools, correlate signals, identify the most likely root cause, and recommend remediation steps.

The system is designed around a simple principle:

```text
READ → INVESTIGATE → CORRELATE → EXPLAIN → RECOMMEND
```

CloudOps AI operates in **read-only mode**. It does not automatically modify production systems or execute remediation actions.

---

## Why CloudOps AI?

When a production service becomes slow or starts failing, engineers typically need to investigate several independent sources:

```text
Metrics
   ↓
Logs
   ↓
Database
   ↓
Recent Deployments
   ↓
Runbooks / Documentation
```

The difficult part isn't accessing each source individually.

The difficult part is **correlating the evidence**.

For example:

> "Payment API latency has suddenly increased."

An engineer might need to determine:

* Did request latency increase?
* Is the database slow?
* Are CPU or memory resources exhausted?
* Are errors increasing?
* Did a recent deployment introduce a change?
* Are application logs showing a specific failing query?
* Does the service runbook contain relevant troubleshooting guidance?
* Which signal is the actual bottleneck?
* What should be done next?

CloudOps AI is designed to automate this investigation process.

---

## Core Concept

```text
                        Production Incident
                                │
                                ▼
                       ┌─────────────────┐
                       │   CloudOps AI   │
                       │   AI Agent      │
                       └────────┬────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
          Metrics             Logs          Deployments
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │     RAG     │
                         │  Runbooks   │
                         │  Knowledge  │
                         └──────┬──────┘
                                │
                                ▼
                     Evidence Correlation
                                │
                                ▼
                      Root Cause Analysis
                                │
                                ▼
                       Recommendation
```

The important part is that the LLM is not simply answering:

> "What do you think caused this?"

Instead, the agent decides which tools it needs, gathers operational evidence, and reasons over that evidence.

---

## Example Investigation

### Incident

```text
The Payment API latency has suddenly increased.
Investigate the issue.
```

### Metrics

```text
API P95 latency:       5800 ms
API P99 latency:       7200 ms
Database latency:      4900 ms
CPU utilization:       42%
Memory utilization:    58%
Error rate:            1.2%
Throughput:            842 requests/sec
```

### Logs

```text
database query latency=3200ms query=payment_lookup
database query latency=3700ms query=payment_lookup
database query latency=4100ms query=payment_lookup
database query latency=4500ms query=payment_lookup
request latency=5800ms endpoint=/payments
request timeout endpoint=/payments
```

### Deployment

```text
Version:          v1.8.3
Previous:         v1.8.2

Changes:
- Updated payment_lookup query
- Added transaction metadata filtering
```

### Agent Reasoning

```text
Deployment
    │
    ├── v1.8.3 deployed at 18:15
    │
    ▼
Database query latency begins increasing
    │
    ├── payment_lookup: 3.2s → 3.7s → 4.1s → 4.5s
    │
    ▼
Database latency reaches 4.9s
    │
    ▼
API P95 reaches 5.8s
    │
    ▼
Requests begin timing out
```

### Result

```text
Likely Root Cause:
The modified payment_lookup query introduced in v1.8.3
is the most likely cause of the database latency increase.

Confidence:
High

Recommendation:
Investigate the query execution plan and index usage.
Consider rollback to v1.8.2 if customer impact is significant,
subject to human approval.
```

The agent must distinguish between **observed evidence** and **hypotheses**.

For example, it should not claim:

```text
"The query is definitely missing an index."
```

unless the system has actually inspected the database execution plan.

Instead:

```text
"The evidence strongly suggests a query-level performance
regression. Missing indexes or a changed execution plan should
be investigated."
```

---

## Architecture

### Current MVP

The initial version uses local mock operational data so the complete agentic investigation workflow can be developed without requiring paid cloud infrastructure.

```text
                         ┌────────────────────┐
                         │    FastAPI API     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Google ADK       │
                         │   Agent            │
                         └─────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              Metrics Tool    Logs Tool    Deployment Tool
                    │              │              │
                    ▼              ▼              ▼
              Local JSON       Local Log       Local JSON
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                            Gemini Model
                                   │
                                   ▼
                          Investigation Result
```

The local data sources will later be replaced by real production observability systems.

---

## Technology Stack

| Layer            | Technology                 | Purpose                              |
| ---------------- | -------------------------- | ------------------------------------ |
| Language         | Python                     | Core application                     |
| API              | FastAPI                    | Incident API                         |
| AI Model         | Gemini                     | Reasoning and investigation          |
| Agent Framework  | Google ADK                 | Agent orchestration and tool calling |
| RAG              | Embeddings + Vector Search | Runbook and operational knowledge    |
| Logs             | Google Cloud Logging       | Production log investigation         |
| Metrics          | Google Cloud Monitoring    | Production metrics                   |
| Eventing         | Google Cloud Pub/Sub       | Incident-triggered investigations    |
| Storage          | Google Cloud Storage       | Runbooks and operational documents   |
| Database         | PostgreSQL / Cloud SQL     | Incident and application data        |
| Containerization | Docker                     | Application packaging                |
| Deployment       | Cloud Run                  | Application hosting                  |
| CI/CD            | Cloud Build                | Automated deployment                 |
| Security         | IAM + Secret Manager       | Identity and secret management       |
| Testing          | Pytest                     | Unit and integration testing         |
| Load Testing     | k6 / Locust                | Performance testing                  |

The MVP currently focuses on the **free Gemini API + local development workflow**. Cloud infrastructure integrations are introduced incrementally.

---

## Agent Tools

The CloudOps AI agent is designed around tools rather than hard-coded investigation logic.

### Current Tools

```text
get_service_metrics()
        │
        └── Retrieves service performance metrics


search_logs()
        │
        └── Searches application logs


get_recent_deployment()
        │
        └── Retrieves recent deployment information
```

### Planned Tools

```text
search_runbook()
        │
        └── Retrieves relevant operational knowledge
```

Later:

```text
query_cloud_monitoring()
query_cloud_logging()
query_database()
search_incident_history()
```

This allows the agent to decide what information it needs during an investigation.

---

## Agentic Workflow

The agent follows an investigation loop rather than a fixed response template.

```text
Incident
   │
   ▼
Understand problem
   │
   ▼
Identify service
   │
   ▼
Gather evidence
   │
   ├──── Metrics
   │
   ├──── Logs
   │
   ├──── Deployment
   │
   └──── Runbook
   │
   ▼
Correlate signals
   │
   ▼
Generate possible causes
   │
   ▼
Eliminate unsupported causes
   │
   ▼
Select most likely cause
   │
   ▼
Assign confidence
   │
   ▼
Recommend remediation
```

The agent must never invent evidence.

---

## Root Cause Analysis Model

CloudOps AI separates investigation into several layers.

### 1. Symptoms

What is happening?

```text
P95 latency increased
Request timeouts increased
Database latency increased
```

### 2. Signals

Where is the problem visible?

```text
API
Database
Application logs
Deployment history
```

### 3. Correlation

Do the signals line up in time and behavior?

```text
Deployment
      ↓
Query modification
      ↓
Database latency
      ↓
API latency
      ↓
Timeouts
```

### 4. Hypothesis

What is the most likely explanation?

```text
Query performance regression
```

### 5. Confidence

How strong is the evidence?

```text
High
Medium
Low
```

### 6. Missing Evidence

What would be required to confirm the hypothesis?

```text
EXPLAIN ANALYZE
Query execution plan
Index usage
Database query statistics
```

This prevents the agent from confusing correlation with proof.

---

## RAG / Operational Knowledge

A major part of CloudOps AI is giving the agent access to operational knowledge.

Example:

```text
data/runbooks/payment-api.md
```

The runbook can contain:

```text
- High latency troubleshooting
- Database troubleshooting
- Known failure modes
- Deployment procedures
- Index recommendations
- Recovery procedures
```

The RAG pipeline will eventually work as:

```text
Runbooks / Documents
        │
        ▼
Document Loader
        │
        ▼
Chunking
        │
        ▼
Embeddings
        │
        ▼
Vector Store
        │
        ▼
Retriever
        │
        ▼
search_runbook()
        │
        ▼
Gemini Agent
```

This allows CloudOps AI to combine **live operational evidence** with **organizational knowledge**.

---

## Planned Production Architecture

Once the local MVP is stable, the mock sources will be replaced with real cloud services.

```text
                         ┌──────────────────┐
                         │ Incident Source  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Google Pub/Sub   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ CloudOps AI      │
                         │ Agent            │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       Cloud Monitoring    Cloud Logging        Deployment Data
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                           RAG / Runbooks
                                  │
                                  ▼
                         Evidence Correlation
                                  │
                                  ▼
                              Gemini
                                  │
                                  ▼
                         Incident Report
```

---

## Safety Model

CloudOps AI is intentionally designed as a **read-only incident investigator** in the initial versions.

### The Agent Can

```text
✓ Read metrics
✓ Read logs
✓ Read deployment information
✓ Search operational documentation
✓ Analyze incidents
✓ Identify likely causes
✓ Recommend remediation
```

### The Agent Cannot

```text
✗ Deploy code
✗ Roll back deployments
✗ Modify databases
✗ Restart services
✗ Change infrastructure
✗ Modify production configuration
```

Any production-changing recommendation requires human approval and execution.

Future autonomous remediation, if ever introduced, should use explicit permissions, safeguards, approval policies, and auditability.

---

## Project Structure

```text
cloudops-ai/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── incidents.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── cloudops_agent.py
│   │   └── test_agent.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── logs.py
│   │   └── deployments.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── embeddings.py
│   │   ├── store.py
│   │   └── retriever.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── incident.py
│   │
│   └── services/
│       └── __init__.py
│
├── data/
│   ├── logs/
│   │   └── payment-api.log
│   │
│   ├── metrics/
│   │   └── payment-api.json
│   │
│   ├── deployments/
│   │   └── payment-api.json
│   │
│   └── runbooks/
│       └── payment-api.md
│
├── tests/
│   └── __init__.py
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Development Roadmap

CloudOps AI will be developed incrementally.

### Milestone 1 — Backend Foundation

* [x] FastAPI application
* [x] Health endpoint
* [x] Incident API
* [x] Pydantic incident model
* [x] Project configuration
* [x] Docker setup
* [x] Mock operational data

### Milestone 2 — Agentic Investigation

* [x] Gemini integration
* [x] Google ADK integration
* [x] CloudOps AI agent
* [x] Metrics tool
* [x] Logs tool
* [x] Deployment tool
* [x] Tool-based investigation
* [x] Evidence correlation
* [x] Root-cause analysis
* [x] Confidence assessment
* [x] Read-only safety model

### Milestone 3 — RAG

* [ ] Runbook document loader
* [ ] Document chunking
* [ ] Embedding generation
* [ ] Vector store
* [ ] Semantic retrieval
* [ ] `search_runbook()` tool
* [ ] Integrate RAG with the agent
* [ ] Evidence + operational knowledge reasoning

### Milestone 4 — Real Observability

Replace local mock data with real production observability sources.

* [ ] Google Cloud Monitoring integration
* [ ] Google Cloud Logging integration
* [ ] Real deployment metadata
* [ ] Time-window based log investigation
* [ ] Metric anomaly investigation
* [ ] Production evidence correlation

### Milestone 5 — Event-Driven Investigation

Introduce automatic incident triggering.

```text
Monitoring Alert
      ↓
Google Pub/Sub
      ↓
CloudOps AI
      ↓
Investigation
      ↓
RCA
      ↓
Incident Report
```

Tasks:

* [ ] Pub/Sub integration
* [ ] Alert ingestion
* [ ] Automatic investigation trigger
* [ ] Incident lifecycle
* [ ] Investigation status
* [ ] Persistent incident records

### Milestone 6 — Productionization

* [ ] PostgreSQL / Cloud SQL
* [ ] Cloud Run deployment
* [ ] Secret Manager
* [ ] IAM permissions
* [ ] Cloud Build CI/CD
* [ ] Structured logging
* [ ] Error handling
* [ ] Retry mechanisms
* [ ] Authentication
* [ ] Unit tests
* [ ] Integration tests
* [ ] Agent evaluation tests
* [ ] Load testing with k6 / Locust
* [ ] Observability for CloudOps AI itself

---

## Testing Strategy

CloudOps AI will be tested at multiple levels.

### Unit Tests

Test individual tools:

```text
get_service_metrics()
search_logs()
get_recent_deployment()
search_runbook()
```

### Agent Tests

Test whether the agent:

* Calls appropriate tools
* Uses tool results correctly
* Avoids inventing evidence
* Distinguishes facts from hypotheses
* Produces consistent RCA reports

### Incident Scenarios

Example scenarios:

```text
1. Database latency increase
2. CPU saturation
3. Memory pressure
4. Error-rate spike
5. Failed deployment
6. Dependency latency
7. Network-related degradation
8. Insufficient evidence
```

### Load Testing

The API will eventually be tested using:

```text
k6
```

or:

```text
Locust
```

Metrics to evaluate include:

```text
Requests/sec
Concurrency
P50 latency
P95 latency
P99 latency
Error rate
Throughput
```

---

## Example API

### Create Incident

```http
POST /incidents/
Content-Type: application/json
```

Request:

```json
{
  "service": "payment-api",
  "description": "Payment API latency has suddenly increased",
  "severity": "high"
}
```

Response:

```json
{
  "message": "Incident received",
  "incident": {
    "service": "payment-api",
    "description": "Payment API latency has suddenly increased",
    "severity": "high"
  }
}
```

---

## Local Development

### Clone the Repository

```bash
git clone https://github.com/<your-username>/cloudops-ai.git
cd cloudops-ai
```

### Create Virtual Environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
APP_NAME=CloudOps AI
ENVIRONMENT=development

GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

Do not commit `.env` to GitHub.

The `.env` file should remain in `.gitignore`.

---

## Run the FastAPI Application

```bash
uvicorn app.main:app --reload
```

The API will be available locally at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

## Run the AI Agent

```bash
python -m app.agents.test_agent
```

Example:

```text
Starting CloudOps AI investigation...

## Incident

The Payment API is experiencing increased latency...

## Affected Service

payment-api

## Observed Evidence

...

## Investigation

...

## Likely Root Cause

...

## Confidence

High

## Recommendation

...
```

---

## Environment and Security

Sensitive configuration should never be committed to the repository.

The following files should remain local:

```text
.env
```

Use:

```text
.env.example
```

for documenting required environment variables.

Never commit:

```text
API keys
Service account credentials
Passwords
Database credentials
Access tokens
Private keys
```

Production secrets will eventually be managed using **Google Secret Manager**.

---

## Design Principles

### Evidence First

The agent should gather evidence before reaching conclusions.

### No Hallucinated Observability

If a metric, log, deployment, or operational fact was not observed, the agent must not invent it.

### Correlation Over Guessing

The agent should correlate:

```text
Time
+
Metrics
+
Logs
+
Deployments
+
Operational Knowledge
```

before selecting a root cause.

### Confidence Matters

Every RCA should communicate how strong the evidence is.

### Read-Only by Default

The initial system investigates and recommends. It does not modify production.

### Human-in-the-Loop

Production-changing actions require human approval.

### Incremental Architecture

The system starts with local data and gradually moves toward real cloud infrastructure.

---

## Future Capabilities

Potential future extensions include:

```text
Incident History
      ↓
Similar Incident Detection
      ↓
Previous RCA Retrieval
      ↓
Faster Investigation
```

Additional possibilities:

* Historical incident analysis
* Service dependency graphs
* Anomaly detection
* Deployment risk analysis
* Automatic incident summarization
* Slack / ChatOps integration
* PagerDuty integration
* Alert deduplication
* Incident timeline generation
* Change-impact analysis
* Multi-service investigations
* Human-approved remediation workflows
* Post-incident report generation

Autonomous remediation will only be considered after strong safety controls, permissions, auditing, and evaluation are established.

---

## Project Status

**Current Status: Active Development**

```text
Milestone 1   ████████████████████  Complete
Milestone 2   ████████████████████  Complete
Milestone 3   ░░░░░░░░░░░░░░░░░░░░  Next
Milestone 4   ░░░░░░░░░░░░░░░░░░░░  Planned
Milestone 5   ░░░░░░░░░░░░░░░░░░░░  Planned
Milestone 6   ░░░░░░░░░░░░░░░░░░░░  Planned
```

The current implementation successfully demonstrates:

```text
Incident
   ↓
Gemini Agent
   ↓
Tool Calling
   ↓
Metrics + Logs + Deployment
   ↓
Evidence Correlation
   ↓
Root Cause Analysis
   ↓
Human-approved Recommendation
```

The next major milestone is **RAG-powered operational knowledge retrieval**.

---

## License

This project is currently intended as an engineering and learning project.

License information will be added as the project evolves.

---

## Author

**Srinu**

Building CloudOps AI as an exploration of:

```text
Agentic AI
+
Site Reliability Engineering
+
Observability
+
System Design
+
Cloud Infrastructure
```

---
