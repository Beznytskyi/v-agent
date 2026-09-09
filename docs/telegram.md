# Telegram Gateway

Telegram is the first user-facing channel for V-Agent. It is an adapter, not part of the agent core.

```text
Telegram user
    |
    v
Telegram Gateway
    |
    v
V-Agent API /agent/run
    |
    v
Planner -> Orchestrator -> Agents / Tools
```

## Configuration

Set these environment variables on the V-Agent host:

```text
V_AGENT_TELEGRAM_ENABLED=true
V_AGENT_TELEGRAM_BOT_TOKEN=<secret>
V_AGENT_TELEGRAM_ALLOWED_USER_IDS=<telegram_numeric_user_id>
```

Multiple users can be allowlisted with comma-separated numeric IDs.

Never commit the bot token or user IDs to the repository.

## Current gateway behavior

- `/start` — initialize the bot conversation.
- `/help` — show supported commands.
- `/new` — start a new task prompt.
- Any other text is treated as an objective for V-Agent.
- Unauthorized Telegram users are rejected before an agent run is started.

## Architecture rule

The gateway must remain channel-specific only. Agent planning, execution, memory, tools, permissions and business logic stay inside V-Agent Core/API.

The initial adapter is deliberately transport-agnostic so Telegram polling/webhook implementation can be added without coupling the core to a Telegram framework.

## Next step

Before production deployment, add durable execution and a worker/queue layer so long-running Telegram tasks can report `accepted`, `running`, `completed` and `error` states and recover after process restarts.
