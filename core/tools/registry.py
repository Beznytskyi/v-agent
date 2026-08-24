from core.tools.gateway import ToolGateway
from core.tools.protocol import Tool
from core.tools.web_research import WebResearchTool


class ToolRegistry:
    """Application-level registry that owns the configured ToolGateway."""

    def __init__(self, tools: list[Tool] | None = None) -> None:
        self.gateway = ToolGateway()
        for tool in tools or []:
            self.gateway.register(tool)

    @classmethod
    def default(cls) -> "ToolRegistry":
        return cls([WebResearchTool()])

    def register(self, tool: Tool) -> None:
        self.gateway.register(tool)

    def names(self) -> list[str]:
        return self.gateway.available()
