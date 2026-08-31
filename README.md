# V-Agent

Self-hosted personal AI agent platform.

## Architecture

V-Agent is designed as a modular monolith with background workers and a controlled Tool Gateway.

Core components:
- FastAPI API
- PostgreSQL + pgvector
- Redis
- Celery worker
- Scheduler
- MinIO object storage
- Agent / Planner / Memory / Policy / Tools modules

## Local development

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. API health: `http://localhost:8000/health`.
4. API docs: `http://localhost:8000/docs`.

## Current milestone

**Foundation v0.6 — Planner**

Implemented:
- typed planner contract with `AgentPlan` and `PlanStep`
- provider boundary for future LLM-backed planning
- deterministic safe baseline planner
- orchestrator integration for automatic agent selection
- optional `agent_name` on `POST /agent/run`; omitted means Planner selects the agent
- planned web-research step when a URL and registered tool are available
- planner unit tests

The Planner does not execute tools. Execution remains owned by the Orchestrator and controlled Tool Gateway.

## Next

Add a production LLM provider adapter that emits validated structured plans, with schema validation, timeout/retry policy, and tests.