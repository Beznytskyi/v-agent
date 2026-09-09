from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AgentApiError(RuntimeError):
    """Raised when the V-Agent HTTP API cannot complete a request."""


def _post_agent_run(url: str, objective: str, timeout: float) -> dict[str, Any]:
    payload = json.dumps({"objective": objective}).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        # Keep response details out of user-facing Telegram messages.
        raise AgentApiError(f"V-Agent API returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise AgentApiError("V-Agent API request failed") from exc

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentApiError("V-Agent API returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise AgentApiError("V-Agent API returned an invalid response")
    return result


class VAgentApiClient:
    """Minimal client used by the Telegram channel adapter."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def run(self, objective: str) -> dict[str, Any]:
        if not objective.strip():
            raise ValueError("objective is required")
        return await asyncio.to_thread(
            _post_agent_run,
            f"{self.base_url}/agent/run",
            objective.strip(),
            self.timeout,
        )
