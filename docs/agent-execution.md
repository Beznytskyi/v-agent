# Agent Execution

## Runtime flow

1. `POST /agent/run` creates an `AgentRun`.
2. The API builds an `AgentContext` from the request.
3. `Orchestrator` resolves the requested agent by name.
4. The agent returns a structured `AgentResult`.
5. The result is persisted through `AgentRunService`.
6. Failures are persisted as `failed` runs and exposed as an API error.

## Current agents

- `research` — initial research workflow contract. It currently validates and structures a research request; external web retrieval is intentionally deferred to the Tool Gateway milestone.

## Next milestone

Tool Gateway will provide controlled external capabilities without coupling agents directly to provider SDKs.
