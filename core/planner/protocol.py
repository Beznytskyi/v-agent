from dataclasses import dataclass, field
from typing import Any, Protocol

from core.orchestrator.protocol import AgentContext


@dataclass(frozen=True, slots=True)
class PlanStep:
    """A planned action; execution remains owned by the orchestrator/tool gateway."""

    kind: str
    target: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentPlan:
    agent_name: str
    steps: list[PlanStep] = field(default_factory=list)
    rationale: str = ""


class PlannerProvider(Protocol):
    async def plan(self, context: AgentContext, available_agents: list[str], available_tools: list[str]) -> AgentPlan: ...
