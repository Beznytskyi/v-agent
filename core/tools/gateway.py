from core.tools.protocol import Tool, ToolContext, ToolResult


class ToolGateway:
    """Single execution boundary for all agent tools.

    The gateway deliberately owns permission checks so callers cannot bypass
    tool policy by invoking a tool directly through the registry.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.spec.name
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = tool

    def available(self) -> list[str]:
        return sorted(self._tools)

    def specs(self) -> list:
        return [self._tools[name].spec for name in self.available()]

    async def execute(
        self, name: str, context: ToolContext, arguments: dict
    ) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(status="error", error=f"Unknown tool: {name}")

        missing = tool.spec.permissions - context.permissions
        if missing:
            return ToolResult(
                status="denied",
                error=f"Missing permissions: {sorted(missing)}",
            )

        try:
            return await tool.execute(context, arguments)
        except Exception as exc:
            return ToolResult(status="error", error=str(exc))
