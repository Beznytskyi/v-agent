"""LLM-backed planner provider with strict validation and retry handling."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.orchestrator.protocol import AgentContext
from core.planner.protocol import AgentPlan, PlanStep, PlannerProvider


class PlannerProviderError(RuntimeError):
    """Raised when an LLM planner cannot produce a valid plan."""


class OpenAICompatiblePlannerProvider(PlannerProvider):
    """Call an OpenAI-compatible chat-completions endpoint and validate its plan.

    The provider is intentionally dependency-free. It expects the model response
    to contain a JSON object with ``agent_name``, ``rationale`` and ``steps``.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 20.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("LLM API key is required")
        if not base_url:
            raise ValueError("LLM base URL is required")
        if not model:
            raise ValueError("LLM model is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def plan(
        self,
        context: AgentContext,
        available_agents: list[str],
        available_tools: list[str],
    ) -> AgentPlan:
        payload = self._build_payload(context, available_agents, available_tools)
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                raw = await asyncio.to_thread(self._request, payload)
                return self._parse_and_validate(raw, available_agents, available_tools)
            except (HTTPError, URLError, TimeoutError, PlannerProviderError, ValueError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(min(2**attempt, 4))

        raise PlannerProviderError("LLM planner failed after retries") from last_error

    def _build_payload(
        self,
        context: AgentContext,
        available_agents: list[str],
        available_tools: list[str],
    ) -> dict[str, Any]:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["agent_name", "rationale", "steps"],
            "properties": {
                "agent_name": {"type": "string"},
                "rationale": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["kind", "target", "arguments"],
                        "properties": {
                            "kind": {"type": "string"},
                            "target": {"type": "string"},
                            "arguments": {"type": "object"},
                        },
                    },
                },
            },
        }
        instructions = (
            "Return ONLY a JSON object matching this schema. "
            "Never invent agents or tools. Planner output is declarative; it does not execute actions.\n"
            f"Available agents: {available_agents}\n"
            f"Available tools: {available_tools}\n"
            f"Schema: {json.dumps(schema, separators=(',', ':'))}"
        )
        return {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "objective": context.objective,
                            "input": context.input,
                            "memory": context.memory,
                            "constraints": context.constraints,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
        }

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def _parse_and_validate(
        self,
        response: dict[str, Any],
        available_agents: list[str],
        available_tools: list[str],
    ) -> AgentPlan:
        try:
            content = response["choices"][0]["message"]["content"]
            data = json.loads(content) if isinstance(content, str) else content
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise PlannerProviderError("LLM response does not contain a valid JSON plan") from exc

        if not isinstance(data, dict):
            raise PlannerProviderError("Planner output must be a JSON object")

        agent_name = data.get("agent_name")
        rationale = data.get("rationale", "")
        steps = data.get("steps")
        if not isinstance(agent_name, str) or agent_name not in available_agents:
            raise PlannerProviderError("Planner selected an unavailable agent")
        if not isinstance(rationale, str) or not isinstance(steps, list):
            raise PlannerProviderError("Planner output has an invalid shape")
        if len(steps) > 32:
            raise PlannerProviderError("Planner produced too many steps")

        validated_steps: list[PlanStep] = []
        for item in steps:
            if not isinstance(item, dict):
                raise PlannerProviderError("Planner step must be an object")
            kind, target, arguments = item.get("kind"), item.get("target"), item.get("arguments", {})
            if not isinstance(kind, str) or not isinstance(target, str) or not isinstance(arguments, dict):
                raise PlannerProviderError("Planner step has an invalid shape")
            if kind == "agent" and target not in available_agents:
                raise PlannerProviderError(f"Planner selected unavailable agent: {target}")
            if kind == "tool" and target not in available_tools:
                raise PlannerProviderError(f"Planner selected unavailable tool: {target}")
            if kind not in {"agent", "tool"}:
                raise PlannerProviderError(f"Planner selected unsupported step kind: {kind}")
            validated_steps.append(PlanStep(kind=kind, target=target, arguments=arguments))

        return AgentPlan(agent_name=agent_name, rationale=rationale, steps=validated_steps)


def planner_from_environment() -> OpenAICompatiblePlannerProvider:
    """Build the production provider from environment configuration."""

    return OpenAICompatiblePlannerProvider(
        api_key=os.environ.get("V_AGENT_LLM_API_KEY", ""),
        base_url=os.environ.get("V_AGENT_LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("V_AGENT_LLM_MODEL", ""),
        timeout_seconds=float(os.environ.get("V_AGENT_LLM_TIMEOUT", "20")),
        max_retries=int(os.environ.get("V_AGENT_LLM_MAX_RETRIES", "2")),
    )
