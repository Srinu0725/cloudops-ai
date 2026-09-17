# CloudOps AI

> **Agentic AI-powered production incident investigation and root-cause analysis platform.**

CloudOps AI is an **Agentic AI system for investigating production incidents automatically**.

Instead of requiring an engineer to manually inspect metrics, logs, recent deployments, and operational documentation, CloudOps AI gathers operational evidence, correlates signals across time, identifies likely root-cause hypotheses, evaluates evidence strength, and generates actionable investigation reports.

The system is designed around:

```text
READ → INVESTIGATE → CORRELATE → EXPLAIN → RECOMMEND
```

CloudOps AI operates in **read-only mode**. It does not automatically modify production systems or execute remediation actions.

---

# Why CloudOps AI?

When a production service becomes slow or starts failing, engineers typically investigate multiple independent sources:

```text
                Production Incident
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
     Metrics           Logs         Deployments
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                  Runbooks / Docs
                        │
                        ▼
                Evidence Correlation
                        │
                        ▼
                  Root Cause Analysis
```

The difficult part is not accessing each source individually.

The difficult part is **correlating the evidence**.

For example:

> Payment API latency has suddenly increased.

The investigation needs to determine:

* Did request latency increase?
* Is the database slow?
* Are CPU or memory resources exhausted?
* Are errors increasing?
* Did a recent deployment introduce a change?
* Are application logs showing slow queries?
* Does the runbook contain relevant troubleshooting guidance?
* Which signals correlate in time?
* What evidence supports the root-cause hypothesis?
* What evidence is still missing?
* What should an engineer investigate next?

CloudOps AI is designed to automate this investigation process while keeping humans responsible for production-changing actions.

---

# Core Concept

```text
                         Production Incident
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   FastAPI API   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Incident Event  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  asyncio Queue  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Background      │
                         │ Worker          │
                         └────────┬────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │ Investigation Engine   │
                     └────────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
           Metrics              Logs             Deployments
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ RAG / Runbooks  │
                         └────────┬────────┘
                                  │
                                  ▼
                         Evidence Correlation
                                  │
                                  ▼
                         Deterministic RCA
                                  │
                                  ▼
                         Confidence Calibration
                                  │
                                  ▼
                         Final Incident Report
```

The LLM/agent is not simply asked:

> "What do you think caused this?"

Instead, the system gathers operational evidence first and uses that evidence to build and evaluate root-cause hypotheses.

---

# Example Investigation

## Incident

```text
The Payment API latency has suddenly increased.

Investigate the issue.
```

## Observed Metrics

```text
API P50 latency:       420 ms
API P95 latency:      5800 ms
API P99 latency:      7200 ms

Database latency:     4900 ms

CPU utilization:        42%
Memory utilization:     58%

Error rate:              1.2%
Throughput:              842 requests/sec
```

The investigation engine compares the current observations with historical baseline data.

Example baseline:

```text
Metric              Baseline      Current
------------------------------------------------
DB latency             390 ms       4900 ms
P95 latency            415 ms       5800 ms
P99 latency            445 ms       7200 ms
Error rate              0.2%          1.2%
CPU                      40%            42%
Memory                   54%            58%
RPS                     ~798           842
```

This allows the system to distinguish service degradation from relatively stable resource utilization.

---

# Log Evidence

Example time-windowed logs:

```text
18:18:12  deployment version=v1.8.3

18:21:44  database query latency=3200ms
          query=payment_lookup

18:23:18  database query latency=3700ms
          query=payment_lookup

18:24:01  database query latency=4100ms
          query=payment_lookup

18:25:42  database query latency=4500ms
          query=payment_lookup

18:27:33  request latency=5800ms
          endpoint=/payments

18:28:14  database connection duration=4700ms

18:29:51  database connection duration=4900ms

18:30:00  request timeout
          endpoint=/payments
```

---

# Deployment Evidence

```text
Version:          v1.8.3
Previous Version: v1.8.2

Changes:

- Updated payment lookup query
- Added transaction metadata filtering
```

---

# Investigation Timeline

CloudOps AI constructs a chronological incident timeline:

```text
18:15
Deployment v1.8.3
       │
       ▼
18:20
First metric degradation
       │
       ▼
18:21
payment_lookup query slows
       │
       ▼
18:25
API/database latency increases significantly
       │
       ▼
18:27
API request latency reaches 5.8 seconds
       │
       ▼
18:30
Payment request timeout
```

This temporal correlation is used as evidence when evaluating root-cause hypotheses.

---

# Root Cause Analysis

CloudOps AI separates:

```text
Observed Evidence
        ↓
Correlation
        ↓
Hypothesis
        ↓
Confidence
        ↓
Missing Evidence
        ↓
Recommended Investigation
```

Example:

```text
Likely Root Cause:

A query-level performance regression associated with
the payment_lookup changes introduced in v1.8.3.
```

The system deliberately avoids unsupported claims.

For example, it should **not** claim:

```text
"The query definitely has a missing index."
```

unless the database execution plan actually proves that.

Instead:

```text
"The evidence strongly suggests a query-level performance
regression. Query execution plans and index usage should
be investigated to confirm the cause."
```

---

# Evidence Model

CloudOps AI categorizes investigation evidence into multiple sources:

```text
1. Metrics
2. Application Logs
3. Deployment History
4. Operational Runbooks
```

Evidence is collected with information such as:

```text
Evidence Type
Source
Observation
Strength
Timestamp
Supporting Data
```

Important distinction:

> Evidence strength indicates how relevant and directly observed the evidence is. It does not automatically establish causality.

Causality is evaluated separately by the RCA layer.

---

# Metric Analysis

The observability engine currently analyzes **8 service-health signals**:

```text
1. P50 latency
2. P95 latency
3. P99 latency
4. Request throughput
5. Error rate
6. CPU utilization
7. Memory utilization
8. Database latency
```

Historical observations are used to construct a baseline.

The system can identify deviations such as:

```text
Database latency:
390 ms → 4900 ms

P95 latency:
415 ms → 5800 ms

P99 latency:
445 ms → 7200 ms

Error rate:
0.2% → 1.2%
```

The analyzer also avoids treating every change as an anomaly.

For example, a small increase in request throughput does not automatically indicate an incident.

---

# Baseline-Aware Anomaly Detection

The investigation engine uses historical observations immediately preceding the incident window as the baseline.

Conceptually:

```text
Historical Data
      │
      ▼
Baseline
      │
      ▼
Current Incident Window
      │
      ▼
Compare
      │
      ▼
Detect Anomalies
```

This is more useful than comparing the current value against a fixed hard-coded threshold because normal service behavior can vary between systems.

---

# RAG / Operational Knowledge

CloudOps AI includes a local RAG pipeline for operational documentation.

Current pipeline:

```text
Runbook / Documentation
          │
          ▼
    Document Loader
          │
          ▼
   Section-Aware Chunking
          │
          ▼
 Sentence Transformer
   Embeddings
          │
          ▼
     FAISS Vector Store
          │
          ▼
      Retriever
          │
          ▼
    search_runbook()
          │
          ▼
 Investigation Engine
```

Current embedding model:

```text
all-MiniLM-L6-v2
```

The vector store uses normalized embeddings with similarity search.

Runbook retrieval is performed using investigation-specific queries such as:

```text
payment-api high latency database latency error rate troubleshooting
```

and:

```text
payment-api slow database query payment_lookup investigation
```

This allows operational knowledge to be retrieved based on the incident rather than blindly passing the entire runbook to the model.

---

# Investigation Summary

The investigation engine produces an intermediate structured summary containing:

```text
Incident
Service
Investigation Window
Baseline
Current Metrics
Anomalies
Logs
Deployment
Timeline
Evidence
Runbook Context
```

This summary becomes the evidence package used by the RCA layer.

---

# Deterministic RCA

CloudOps AI does not rely entirely on LLM reasoning for root-cause analysis.

A deterministic RCA layer evaluates observable relationships such as:

```text
Database anomaly
        +
Slow database query
        +
Recent query-related deployment
        +
API latency anomaly
        +
Temporal correlation
```

These signals are combined into root-cause hypotheses.

The result distinguishes between:

```text
Observed
```

and:

```text
Inferred
```

This helps reduce unsupported conclusions.

---

# Confidence Calibration

Each root-cause hypothesis receives an evidence-supported confidence assessment.

The calibration considers factors such as:

```text
Metric anomalies
Database latency anomaly
API latency anomaly
Slow query evidence
Deployment query changes
Missing diagnostic evidence
```

Confidence is reported as:

```text
HIGH
MEDIUM
LOW
```

The confidence score represents **evidence-supported confidence**, not a statistical probability that the hypothesis is correct.

---

# Missing Evidence

A key design feature is explicitly identifying what the system does **not** know.

For the payment-api example, the system may identify missing evidence such as:

```text
- EXPLAIN ANALYZE output
- Query execution plan
- Index usage
- Database CPU
- Database I/O
- Lock contention
- Query statistics
```

This prevents the investigation from turning an incomplete hypothesis into a false certainty.

---

# Final Incident Report

The investigation produces a structured final report containing:

```text
Report Version
Affected Service
Incident
Investigation Window
Impact
Timeline
Observed Evidence
Root-Cause Hypotheses
Limitations
Missing Evidence
Runbook Guidance
Recommended Next Steps
```

The report is designed to be consumed by an engineer, API client, or future incident-management interface.

---

# Event-Driven Architecture

CloudOps AI now supports an asynchronous event-driven investigation workflow.

Current local architecture:

```text
POST /incidents
      │
      ▼
IncidentEvent
      │
      ▼
asyncio.Queue
      │
      ▼
IncidentWorker
      │
      ▼
Investigation
      │
      ▼
RCA
      │
      ▼
Final Report
```

The current implementation uses a local `asyncio.Queue`.

This allows incident ingestion to be separated from potentially longer-running investigation work.

---

# Incident Lifecycle

Each incident has a tracked lifecycle.

```text
CREATED
   │
   ▼
INVESTIGATING
   │
   ▼
ANALYZING
   │
   ▼
RCA
   │
   ▼
REPORT_GENERATED
   │
   ▼
COMPLETED
```

Failures transition the incident into:

```text
FAILED
```

The system tracks timestamps such as:

```text
created_at
started_at
completed_at
failed_at
```

This provides the foundation for future persistent incident history and retry handling.

---

# Incident API

## Create Incident

```http
POST /incidents
Content-Type: application/json
```

Example request:

```json
{
  "service": "payment-api",
  "description": "Payment API latency has suddenly increased",
  "severity": "high",
  "start_time": "2026-09-15T18:20:00Z",
  "end_time": "2026-09-15T18:30:00Z"
}
```

The API responds with an accepted incident:

```json
{
  "incident_id": "generated-id",
  "status": "CREATED",
  "message": "Incident created and queued for investigation."
}
```

The endpoint returns HTTP:

```text
202 Accepted
```

because investigation happens asynchronously.

---

## Get Incident Status

```http
GET /incidents/{incident_id}/status
```

Example:

```json
{
  "incident_id": "abc123",
  "service": "payment-api",
  "status": "INVESTIGATING",
  "stage": "ANALYZING",
  "created_at": "...",
  "started_at": "...",
  "completed_at": null,
  "failed_at": null,
  "error": null
}
```

---

## Get Incident

```http
GET /incidents/{incident_id}
```

Returns the complete incident state, including the final investigation report once processing is complete.

---

# Agent Tools

The agent is designed around tools rather than hard-coded answers.

Current operational tools include:

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


investigate_incident()
        │
        └── Runs the complete evidence-driven investigation
```

The RAG system additionally provides operational knowledge retrieval through the runbook search pipeline.

---

# Agentic Workflow

The investigation follows an evidence-first workflow:

```text
Incident
   │
   ▼
Understand Problem
   │
   ▼
Identify Service
   │
   ▼
Collect Evidence
   │
   ├── Metrics
   ├── Logs
   ├── Deployment
   └── Runbook
   │
   ▼
Build Timeline
   │
   ▼
Analyze Baseline
   │
   ▼
Detect Anomalies
   │
   ▼
Correlate Evidence
   │
   ▼
Generate Hypotheses
   │
   ▼
Evaluate Evidence
   │
   ▼
Calibrate Confidence
   │
   ▼
Identify Missing Evidence
   │
   ▼
Generate Recommendations
   │
   ▼
Final Incident Report
```

The system must never invent operational evidence.

---

# Safety Model

CloudOps AI is intentionally designed as a **read-only incident investigator**.

## The System Can

```text
✓ Read metrics
✓ Read logs
✓ Read deployment information
✓ Search operational documentation
✓ Analyze incidents
✓ Detect anomalies
✓ Correlate evidence
✓ Generate root-cause hypotheses
✓ Assign evidence-supported confidence
✓ Recommend remediation
```

## The System Cannot

```text
✗ Deploy code
✗ Roll back deployments
✗ Modify databases
✗ Restart services
✗ Change infrastructure
✗ Modify production configuration
```

Production-changing actions require human approval and execution.

---

# Technology Stack

| Layer            | Technology                 | Purpose                              |
| ---------------- | -------------------------- | ------------------------------------ |
| Language         | Python                     | Core application                     |
| API              | FastAPI                    | Incident ingestion and APIs          |
| Agent Framework  | Google ADK                 | Agent orchestration                  |
| AI Model         | Gemini                     | Agent reasoning                      |
| RAG              | Sentence Transformers      | Semantic embeddings                  |
| Vector Search    | FAISS                      | Runbook retrieval                    |
| Observability    | Local provider abstraction | Metrics, logs, deployments           |
| Event Queue      | asyncio.Queue              | Local asynchronous event processing  |
| Worker           | Python asyncio             | Background incident processing       |
| Database         | PostgreSQL                 | Planned persistent incident storage  |
| ORM              | SQLAlchemy Async           | Planned database access              |
| Migrations       | Alembic                    | Planned schema migrations            |
| Containerization | Docker                     | Application/infrastructure packaging |
| Testing          | Pytest                     | Automated testing                    |
| Load Testing     | k6 / Locust                | Planned performance testing          |

---

# Current vs Planned Infrastructure

The current implementation intentionally avoids requiring paid cloud infrastructure.

## Currently Implemented

```text
FastAPI
Google ADK
Gemini integration
Local observability provider
Local metrics
Local logs
Local deployments
Local runbooks
Sentence Transformers
FAISS
Evidence correlation
RCA engine
Confidence calibration
Incident events
asyncio.Queue
Background worker
Incident lifecycle tracking
```

## Planned Production Integrations

```text
Google Cloud Monitoring
Google Cloud Logging
Google Pub/Sub
Cloud Storage
Cloud SQL / PostgreSQL
Cloud Run
IAM
Secret Manager
Cloud Build
```

The local architecture is designed so these components can be introduced incrementally.

---

# Project Structure

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
│   │   ├── test_agent.py
│   │   └── test_gemini.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── logs.py
│   │   ├── deployments.py
│   │   └── investigation.py
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── time_utils.py
│   │   ├── analyzer.py
│   │   ├── timeline.py
│   │   ├── evidence.py
│   │   ├── investigator.py
│   │   ├── summary.py
│   │   ├── rca.py
│   │   ├── confidence.py
│   │   ├── report.py
│   │   ├── reasoner.py
│   │   └── tests
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── store.py
│   │   ├── retriever.py
│   │   └── test_rag.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── incident.py
│   │
│   ├── incidents/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── store.py
│   │   └── service.py
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── bus.py
│   │   ├── handlers.py
│   │   ├── queue.py
│   │   ├── worker.py
│   │   ├── service.py
│   │   └── test_event_flow.py
│   │
│   └── services/
│       └── __init__.py
│
├── data/
│   ├── logs/
│   │   └── payment-api.log
│   ├── metrics/
│   │   └── payment-api.json
│   ├── deployments/
│   │   └── payment-api.json
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

# Development Roadmap

CloudOps AI is being developed incrementally.

## Milestone 1 — Backend Foundation

* [x] FastAPI application
* [x] Health endpoint
* [x] Incident API
* [x] Pydantic request models
* [x] Project configuration
* [x] Docker setup
* [x] Mock operational data

## Milestone 2 — Agentic Investigation

* [x] Gemini integration
* [x] Google ADK integration
* [x] CloudOps AI agent
* [x] Metrics tool
* [x] Logs tool
* [x] Deployment tool
* [x] Tool-based investigation
* [x] Evidence-driven reasoning
* [x] Read-only safety model

## Milestone 3 — RAG

* [x] Runbook document loader
* [x] Section-aware document chunking
* [x] Embedding generation
* [x] FAISS vector store
* [x] Semantic retrieval
* [x] Runbook retrieval
* [x] RAG integration with investigation
* [x] Operational knowledge retrieval

## Milestone 4 — Observability & RCA

* [x] Observability provider abstraction
* [x] Historical metrics
* [x] Baseline calculation
* [x] Anomaly detection
* [x] Time-window-aware log search
* [x] Incident timeline generation
* [x] Evidence collection
* [x] Evidence strength scoring
* [x] Investigation engine
* [x] Investigation summary
* [x] Deterministic RCA
* [x] Confidence calibration
* [x] Missing-evidence identification
* [x] Final incident report
* [x] Gemini reasoning layer with fallback architecture

## Milestone 5 — Event-Driven Investigation

### 5.1 Incident Events

* [x] Incident event model
* [x] Event IDs
* [x] Event metadata
* [x] Event serialization

### 5.2 Incident State

* [x] Incident state model
* [x] Lifecycle tracking
* [x] Investigation timestamps
* [x] Report storage
* [x] Failure state

### 5.3 FastAPI Incident API

* [x] Incident creation
* [x] Incident status endpoint
* [x] Incident retrieval endpoint
* [x] HTTP 202 asynchronous ingestion

### 5.4 Background Processing

* [x] FastAPI background worker integration
* [x] Asynchronous incident processing
* [x] Investigation execution outside request lifecycle

### 5.5 Local Event Queue

* [x] asyncio.Queue
* [x] Event publishing
* [x] Event consumption
* [x] Worker loop
* [x] Queue size tracking

### 5.6 Incident Lifecycle

* [x] CREATED
* [x] INVESTIGATING
* [x] ANALYZING
* [x] RCA
* [x] REPORT_GENERATED
* [x] COMPLETED
* [x] FAILED
* [x] Error capture
* [x] Lifecycle timestamps

### 5.7 PostgreSQL Persistence

* [ ] PostgreSQL incident persistence
* [ ] SQLAlchemy AsyncSession
* [ ] Incident repository
* [ ] Alembic migrations
* [ ] Persistent incident reports
* [ ] Persistent lifecycle state

## Milestone 5.8 — Reliability

* [ ] Retry handling
* [ ] Failure recovery
* [ ] Dead-letter strategy
* [ ] Worker failure handling

## Milestone 5.9 — Idempotency

* [ ] Duplicate incident detection
* [ ] Idempotent event processing
* [ ] Duplicate investigation prevention

## Milestone 5.10 — Worker Concurrency

* [ ] Multiple workers
* [ ] Concurrent investigations
* [ ] Queue backpressure
* [ ] Concurrency limits

## Milestone 5.11 — API Hardening

* [ ] Authentication
* [ ] Request validation improvements
* [ ] Rate limiting
* [ ] Structured API errors
* [ ] API observability

---

# Milestone 6 — Real Event Infrastructure

The local event queue will eventually be replaced by a production event broker.

Potential architecture:

```text
Monitoring Alert
      │
      ▼
Google Pub/Sub
      │
      ▼
CloudOps AI
      │
      ▼
Investigation Worker
      │
      ▼
Incident Investigation
```

Planned components:

```text
Google Pub/Sub
Google Cloud Monitoring
Google Cloud Logging
Deployment Metadata
PostgreSQL / Cloud SQL
```

---

# Milestone 7 — Productionization

Future production capabilities:

```text
PostgreSQL / Cloud SQL
Cloud Run
IAM
Secret Manager
Cloud Build
Structured Logging
Authentication
Retry Policies
Monitoring
Alerting
```

Testing will include:

```text
Unit Tests
Integration Tests
Agent Evaluation
Load Testing
Failure Testing
Concurrency Testing
```

---

# Testing Strategy

CloudOps AI is tested at multiple levels.

## Unit Tests

Current test coverage includes components such as:

```text
Metric Analyzer
Log Filtering
Incident Timeline
Evidence Collection
Investigation Engine
RAG Retrieval
Event Flow
```

Example:

```powershell
pytest
```

---

# Investigation Scenarios

The system is designed to handle scenarios such as:

```text
1. Database latency increase
2. CPU saturation
3. Memory pressure
4. Error-rate spike
5. Deployment-related degradation
6. Dependency latency
7. Network-related degradation
8. Insufficient evidence
```

The objective is not to force a root cause.

If evidence is insufficient, the system should explicitly report:

```text
Insufficient Evidence
```

and identify what additional evidence is required.

---

# Load Testing

Performance testing will eventually evaluate:

```text
Requests/sec
Concurrency
P50 latency
P95 latency
P99 latency
Error rate
Throughput
Queue processing time
Worker utilization
```

Potential tools:

```text
k6
Locust
```

No performance claims are made until the system has been benchmarked.

---

# Local Development

## Clone Repository

```bash
git clone <your-repository-url>
cd cloudops-ai
```

## Create Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create:

```text
.env
```

Example:

```env
APP_NAME=CloudOps AI
ENVIRONMENT=development
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

Do not commit `.env`.

Use:

```text
.env.example
```

to document required variables.

Never commit:

```text
API keys
Passwords
Database credentials
Access tokens
Private keys
Service account credentials
```

---

# Run FastAPI

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

# Run Agent Investigation

```bash
python -m app.agents.test_agent
```

The investigation produces structured evidence and RCA information such as:

```text
Affected Service
Investigation Window
Observed Metrics
Anomalies
Logs
Deployment
Timeline
Evidence
Root-Cause Hypotheses
Confidence
Missing Evidence
Recommendations
```

---

# Design Principles

## Evidence First

The system gathers evidence before generating conclusions.

## No Hallucinated Observability

If a metric, log, deployment, or operational fact was not observed, the system must not invent it.

## Correlation Over Guessing

The system correlates:

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

before selecting root-cause hypotheses.

## Confidence Matters

Every hypothesis should communicate the strength of its supporting evidence.

## Missing Evidence Matters

A good investigation identifies what is still required to confirm or reject a hypothesis.

## Read-Only by Default

The system investigates and recommends. It does not modify production.

## Human-in-the-Loop

Production-changing actions require human approval.

## Incremental Architecture

The system starts locally and evolves toward production infrastructure without requiring cloud services during early development.

---

# Future Capabilities

Potential future extensions include:

```text
Historical Incident Search
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
* Deployment risk analysis
* Incident deduplication
* Incident timeline generation
* Change-impact analysis
* Multi-service investigations
* Slack / ChatOps integration
* PagerDuty integration
* Alert deduplication
* Post-incident report generation
* Human-approved remediation workflows

Autonomous remediation will only be considered after strong safety controls, explicit permissions, auditing, and extensive evaluation.

---

# Current Project Status

**Status: Active Development**

```text
Milestone 1       ████████████████████  Complete
Milestone 2       ████████████████████  Complete
Milestone 3       ████████████████████  Complete
Milestone 4       ████████████████████  Complete
Milestone 5.1     ████████████████████  Complete
Milestone 5.2     ████████████████████  Complete
Milestone 5.3     ████████████████████  Complete
Milestone 5.4     ████████████████████  Complete
Milestone 5.5     ████████████████████  Complete
Milestone 5.6     ████████████████████  Complete

Milestone 5.7     ░░░░░░░░░░░░░░░░░░░░  Next
```

### Current capabilities

```text
Incident
   ↓
FastAPI
   ↓
Incident Event
   ↓
Async Queue
   ↓
Background Worker
   ↓
Observability Investigation
   ↓
Metrics + Logs + Deployments
   ↓
Baseline + Anomaly Detection
   ↓
Timeline + Evidence Correlation
   ↓
RAG / Runbooks
   ↓
Deterministic RCA
   ↓
Confidence Calibration
   ↓
Final Incident Report
```

The next milestone is:

> **PostgreSQL Persistence**

This will make incident state and investigation reports durable across application restarts.

---

# License

This project is currently intended as an engineering and learning project.

License information will be added as the project evolves.

---

# Author

**Srinu**

Building CloudOps AI as an exploration of:

```text
Agentic AI
    +
Observability
    +
Site Reliability Engineering
    +
Backend Engineering
    +
System Design
    +
Cloud Infrastructure
```
