from core.tools.protocol import Tool, ToolContext, ToolResult


class ToolGateway:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def available(self) -> list[str]:
        return sorted(self._tools)

    async def execute(self, name: str, context: ToolContext, arguments: dict) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(status="error", error=f"Unknown tool: {name}")
        missing = tool.required_permissions - context.permissions
        if missing:
            return ToolResult(status="denied", error=f"Missing permissions: {sorted(missing)}")
        return await tool.execute(context, arguments)
