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

**Foundation v0.5 — Tool Gateway**

Implemented:
- typed Tool protocol and execution result
- centralized permission gate
- duplicate-safe Tool Gateway registration
- Tool Registry with a default Web Research Tool
- SSRF-conscious public HTTP(S) page retrieval with size/content limits and redirects disabled
- gateway and web-tool tests

The next step is wiring the Tool Registry into the Orchestrator/Research Agent execution path.
