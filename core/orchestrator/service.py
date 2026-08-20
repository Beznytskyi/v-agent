from core.agents.research import ResearchAgent
from core.orchestrator.protocol import AgentContext, AgentResult


class Orchestrator:
    def __init__(self) -> None:
        self.agents = {ResearchAgent.name: ResearchAgent()}

    async def run(self, agent_name: str, context: AgentContext) -> AgentResult:
        agent = self.agents.get(agent_name)
        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        return await agent.run(context)
