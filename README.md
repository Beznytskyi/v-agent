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

**Foundation v0.1** — infrastructure skeleton and core module boundaries.
