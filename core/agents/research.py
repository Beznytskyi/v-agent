from core.orchestrator.protocol import AgentContext, AgentResult


class ResearchAgent:
    name = "research"

    async def run(self, context: AgentContext) -> AgentResult:
        objective = context.objective.strip()
        return AgentResult(
            status="completed",
            summary=f"Research task accepted: {objective}",
            findings=[
                {
                    "type": "research_request",
                    "objective": objective,
                    "source": "agent_input",
                }
            ],
            recommendations=["Connect the web research tool in the next integration milestone."],
        )
