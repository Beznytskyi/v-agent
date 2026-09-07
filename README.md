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
- deterministic safe baseline planner
- OpenAI-compatible LLM planner provider with strict plan validation
- configurable timeout and bounded exponential retry policy
- explicit feature flag for enabling the LLM provider
- provider boundary so deterministic planning remains the safe default
- orchestrator integration for automatic agent selection
- optional `agent_name` on `POST /agent/run`; omitted means Planner selects the agent
- planned web-research step when a URL and registered tool are available
- planner and LLM-provider tests

The Planner does not execute tools. Execution remains owned by the Orchestrator and controlled Tool Gateway. The LLM provider may only select agents and tools that the Orchestrator explicitly exposes.

## LLM configuration

Set `V_AGENT_LLM_ENABLED=true` to explicitly enable the LLM planner. When it is unset or false, V-Agent uses the deterministic safe planner.

Configure the provider with:
- `V_AGENT_LLM_API_KEY`
- `V_AGENT_LLM_BASE_URL` (defaults to `https://api.openai.com/v1`)
- `V_AGENT_LLM_MODEL`
- `V_AGENT_LLM_TIMEOUT` (defaults to `20` seconds)
- `V_AGENT_LLM_MAX_RETRIES` (defaults to `2`)

The LLM provider is never enabled implicitly by the presence of an API key.

## Next

Add end-to-end provider integration coverage with a mocked OpenAI-compatible endpoint, then evaluate enabling the provider in a controlled deployment.