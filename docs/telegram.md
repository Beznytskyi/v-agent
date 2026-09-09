# Telegram Gateway

Telegram is the first user-facing channel for V-Agent. It is an adapter, not part of the agent core.

```text
Telegram user
    |
    v
Telegram Bot API
    |
    v
Long-polling transport
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
V_AGENT_API_BASE_URL=http://127.0.0.1:8000
```

Multiple users can be allowlisted with comma-separated numeric IDs.

Never commit the bot token or user IDs to the repository. The bot token is read only from the environment and is never included in Telegram responses or application errors.

## Current gateway behavior

- `/start` — initialize the bot conversation.
- `/help` — show supported commands.
- `/new` — start a new task prompt.
- Any other text is treated as an objective for V-Agent.
- Unauthorized Telegram users are rejected before an agent run is started.
- Non-text Telegram updates are ignored.

## Long polling

Run the transport locally or on the V-Agent host with:

```bash
python -m apps.telegram.main
```

The transport uses Telegram `getUpdates` with long polling and advances the update offset after each received update. Transient Bot API transport errors are retried without exposing exception details to users.

The implementation uses the Python standard library for HTTP transport, so no Telegram SDK is required at this stage. A webhook adapter can be added later without changing the gateway contract.

## Security boundary

Telegram authentication is based on the numeric Telegram user ID and an explicit allowlist. This is an application authorization boundary; the Telegram bot token is a transport credential and must remain secret.

The current V-Agent `/agent/run` API does not yet require a service authentication token. Therefore the API should be bound to localhost/private network or protected by an external gateway before exposing it publicly. Adding service-to-service authentication is a required hardening step before production exposure.

## Architecture rule

The gateway must remain channel-specific only. Agent planning, execution, memory, tools, permissions and business logic stay inside V-Agent Core/API.

## Next step

Before production deployment, add durable execution and a worker/queue layer so long-running Telegram tasks can report `accepted`, `running`, `completed` and `error` states and recover after process restarts. Then add service-to-service API authentication and webhook support as production hardening.
