# Agent Execution

## Runtime flow

1. `POST /agent/run` creates an `AgentRun`.
2. The API builds an `AgentContext` from the request.
3. `Orchestrator` resolves the requested agent by name.
4. `ResearchAgent` may invoke `web.research` through the Tool Gateway.
5. The Tool Gateway validates the tool permission before execution.
6. The agent returns a structured `AgentResult`.
7. The result is persisted through `AgentRunService`.
8. Failures are persisted as `failed` runs and exposed as an API error.

## Web research

To fetch a public source, an Agent Run supplies:

- `input.url` — the HTTP(S) page to retrieve;
- `context.constraints.permissions` containing `web.read`.

The Web Research Tool is read-only and applies URL scheme, DNS target, redirect, content-type, response-size and output-length limits.

## Current agents

- `research` — first tool-enabled research workflow.

## Next milestone

Planner/LLM integration can build on the controlled Tool Gateway without coupling agents directly to provider SDKs.
