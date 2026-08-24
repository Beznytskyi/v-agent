from types import SimpleNamespace

import pytest

from core.orchestrator.protocol import AgentContext
from core.orchestrator.service import Orchestrator


@pytest.mark.asyncio
async def test_research_agent_completes():
    result = await Orchestrator().run(
        "research",
        AgentContext(objective="Assess the V-Agent market opportunity"),
    )

    assert result.status == "completed"
    assert result.findings
    assert result.findings[0]["type"] == "research_request"


@pytest.mark.asyncio
async def test_research_agent_uses_web_tool(monkeypatch):
    agent = Orchestrator().agents["research"]
    tool = agent.tools.gateway._tools["web.research"]
    monkeypatch.setattr(
        tool,
        "_validate_url",
        lambda url: SimpleNamespace(hostname="example.com"),
    )
    monkeypatch.setattr(tool, "_fetch", lambda url: (b"example text", "text/plain"))

    result = await agent.run(
        AgentContext(
            objective="Read the supplied source",
            input={"url": "https://example.com"},
            constraints={"permissions": ["web.read"]},
        )
    )

    assert result.status == "completed"
    assert result.findings[-1]["type"] == "web_source"
    assert result.findings[-1]["text"] == "example text"


@pytest.mark.asyncio
async def test_research_agent_respects_web_permission_gate():
    result = await Orchestrator().run(
        "research",
        AgentContext(
            objective="Read the supplied source",
            input={"url": "https://example.com"},
        ),
    )

    assert result.status == "completed"
    assert result.findings[0]["type"] == "research_request"
    assert "web.read" in result.recommendations[0]


@pytest.mark.asyncio
async def test_unknown_agent_is_rejected():
    with pytest.raises(ValueError, match="Unknown agent"):
        await Orchestrator().run("unknown", AgentContext(objective="test"))
