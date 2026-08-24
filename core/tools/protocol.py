from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    risk_level: str = "low"
    permissions: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ToolContext:
    permissions: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolResult:
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Tool(Protocol):
    spec: ToolSpec

    async def execute(
        self, context: ToolContext, arguments: dict[str, Any]
    ) -> ToolResult: ...
