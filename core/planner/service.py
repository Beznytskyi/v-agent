from core.orchestrator.protocol import AgentContext
from core.planner.protocol import AgentPlan, PlanStep, PlannerProvider


class DeterministicPlannerProvider:
    """Safe baseline provider used until an LLM adapter is configured."""

    async def plan(self, context: AgentContext, available_agents: list[str], available_tools: list[str]) -> AgentPlan:
        if "research" in available_agents:
            steps: list[PlanStep] = [PlanStep(kind="agent", target="research")]
            if context.input.get("url") and "web.research" in available_tools:
                steps.append(
                    PlanStep(
                        kind="tool",
                        target="web.research",
                        arguments={"url": str(context.input["url"])},
                    )
                )
            return AgentPlan(
                agent_name="research",
                steps=steps,
                rationale="Research is the only currently registered agent; supplied URLs map to web.research.",
            )
        raise ValueError("No planner-compatible agent is registered")


class Planner:
    def __init__(self, provider: PlannerProvider | None = None) -> None:
        self.provider = provider or DeterministicPlannerProvider()

    async def plan(
        self,
        context: AgentContext,
        available_agents: list[str],
        available_tools: list[str],
    ) -> AgentPlan:
        return await self.provider.plan(context, available_agents, available_tools)
