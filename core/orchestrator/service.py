from core.agents.base import AgentContext, AgentResult


class Orchestrator:
    """Coordinates agent execution; policy and tool gateways will be added next."""

    async def run(self, context: AgentContext, agent) -> AgentResult:
        return await agent.run(context)
