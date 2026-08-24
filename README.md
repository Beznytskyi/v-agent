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
- Research Agent integration through the Tool Gateway
- gateway, web-tool and integration tests

Web retrieval is now available when an Agent Run supplies `input.url` and explicitly grants `web.read` in `context.constraints.permissions`.
