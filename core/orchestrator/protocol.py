from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class AgentContext:
    objective: str
    input: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    status: str
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    memory_updates: list[dict[str, Any]] = field(default_factory=list)
    requires_approval: bool = False


class Agent(Protocol):
    name: str

    async def run(self, context: AgentContext) -> AgentResult: ...
