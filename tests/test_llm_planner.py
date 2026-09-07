import json

import pytest

from core.orchestrator.protocol import AgentContext
from core.planner.llm import OpenAICompatiblePlannerProvider, PlannerProviderError


def provider() -> OpenAICompatiblePlannerProvider:
    return OpenAICompatiblePlannerProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="test-model",
        max_retries=0,
    )


def response(plan: dict) -> dict:
    return {"choices": [{"message": {"content": json.dumps(plan)}}]}


def test_llm_provider_accepts_valid_plan(monkeypatch):
    async def fake_request(self, payload):
        return response(
            {
                "agent_name": "research",
                "rationale": "URL requires research",
                "steps": [
                    {"kind": "agent", "target": "research", "arguments": {}},
                    {
                        "kind": "tool",
                        "target": "web.research",
                        "arguments": {"url": "https://example.com"},
                    },
                ],
            }
        )

    monkeypatch.setattr(provider(), "_request", lambda payload: response({
        "agent_name": "research",
        "rationale": "URL requires research",
        "steps": [
            {"kind": "agent", "target": "research", "arguments": {}},
            {"kind": "tool", "target": "web.research", "arguments": {"url": "https://example.com"}},
        ],
    }))

    p = provider()
    monkeypatch.setattr(p, "_request", lambda payload: response({
        "agent_name": "research",
        "rationale": "URL requires research",
        "steps": [
            {"kind": "agent", "target": "research", "arguments": {}},
            {"kind": "tool", "target": "web.research", "arguments": {"url": "https://example.com"}},
        ],
    }))

    plan = __import__("asyncio").run(
        p.plan(
            AgentContext(objective="research", input={"url": "https://example.com"}),
            ["research"],
            ["web.research"],
        )
    )
    assert plan.agent_name == "research"
    assert plan.steps[1].target == "web.research"


def test_llm_provider_rejects_unknown_tool(monkeypatch):
    p = provider()
    monkeypatch.setattr(p, "_request", lambda payload: response({
        "agent_name": "research",
        "rationale": "bad plan",
        "steps": [{"kind": "tool", "target": "shell.exec", "arguments": {}}],
    }))

    with pytest.raises(PlannerProviderError, match="unavailable tool"):
        __import__("asyncio").run(
            p.plan(AgentContext(objective="test"), ["research"], ["web.research"])
        )


def test_llm_provider_rejects_unknown_agent(monkeypatch):
    p = provider()
    monkeypatch.setattr(p, "_request", lambda payload: response({
        "agent_name": "admin",
        "rationale": "bad plan",
        "steps": [],
    }))

    with pytest.raises(PlannerProviderError, match="unavailable agent"):
        __import__("asyncio").run(
            p.plan(AgentContext(objective="test"), ["research"], ["web.research"])
        )
