# V-Agent Architecture v0.1

## Principles

- Self-hosted core; LLM is replaceable infrastructure.
- Modular monolith first; extract services only when justified by scale.
- All external actions go through Tool Gateway and Policy Engine.
- Memory stores facts, events, decisions, entities and semantic context separately.
- High-risk actions require explicit approval.
- Every agent run and tool call is auditable.

## Initial stack

- Python 3.13
- FastAPI
- PostgreSQL + pgvector
- Redis
- Celery
- MinIO / S3-compatible object storage
- Docker Compose

## First workflow

Daily Autonomous Business Brief:

Scheduler -> Job -> Orchestrator -> Memory Context -> specialist agents -> synthesis -> risk detection -> brief -> notification -> memory/audit.
