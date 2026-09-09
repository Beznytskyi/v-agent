import pytest

from core.orchestrator.protocol import AgentContext
from core.planner.service import Planner


@pytest.mark.asyncio
async def test_planner_selects_research_agent():
    plan = await Planner().plan(
        AgentContext(objective="Research V-Agent", input={}),
        available_agents=["research"],
        available_tools=["web.research"],
    )

    assert plan.agent_name == "research"
    assert plan.steps[0].target == "research"


@pytest.mark.asyncio
async def test_planner_adds_web_research_step_for_url():
    plan = await Planner().plan(
        AgentContext(objective="Read source", input={"url": "https://example.com"}),
        available_agents=["research"],
        available_tools=["web.research"],
    )

    assert [step.target for step in plan.steps] == ["research", "web.research"]
    assert plan.steps[1].arguments["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_planner_fails_without_supported_agent():
    with pytest.raises(ValueError, match="No planner-compatible agent"):
        await Planner().plan(
            AgentContext(objective="test"),
            available_agents=[],
            available_tools=[],
        )
