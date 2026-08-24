from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class AgentContext:
    user_id: str
    objective: str
    task: str
    memory: dict[str, Any] = field(default_factory=dict)
    permissions: set[str] = field(default_factory=set)
    available_tools: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentResult:
    status: str
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    requires_approval: bool = False


class Agent(Protocol):
    name: str

    async def run(self, context: AgentContext) -> AgentResult: ...
