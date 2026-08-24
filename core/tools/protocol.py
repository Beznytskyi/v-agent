from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    risk_level: str
    permissions: frozenset[str]


class Tool(Protocol):
    spec: ToolSpec

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]: ...
