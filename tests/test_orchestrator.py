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
async def test_unknown_agent_is_rejected():
    with pytest.raises(ValueError, match="Unknown agent"):
        await Orchestrator().run("unknown", AgentContext(objective="test"))
