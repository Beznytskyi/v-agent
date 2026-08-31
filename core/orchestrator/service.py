from core.agents.research import ResearchAgent
from core.orchestrator.protocol import AgentContext, AgentResult
from core.planner.protocol import AgentPlan
from core.planner.service import Planner


class Orchestrator:
    def __init__(self, planner: Planner | None = None) -> None:
        self.agents = {ResearchAgent.name: ResearchAgent()}
        self.planner = planner or Planner()

    async def plan(self, context: AgentContext) -> AgentPlan:
        return await self.planner.plan(
            context,
            available_agents=sorted(self.agents),
            available_tools=self.agents["research"].tools.names(),
        )

    async def run(self, agent_name: str, context: AgentContext) -> AgentResult:
        agent = self.agents.get(agent_name)
        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        return await agent.run(context)
