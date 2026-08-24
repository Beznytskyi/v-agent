from types import SimpleNamespace

import pytest

from core.tools.gateway import ToolGateway
from core.tools.protocol import ToolContext, ToolResult, ToolSpec
from core.tools.web_research import WebResearchTool


class DummyTool:
    spec = ToolSpec(
        name="dummy",
        description="test tool",
        permissions=frozenset({"dummy.use"}),
    )

    async def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        return ToolResult(status="completed", data=arguments)


@pytest.mark.asyncio
async def test_gateway_denies_missing_permission() -> None:
    gateway = ToolGateway()
    gateway.register(DummyTool())

    result = await gateway.execute("dummy", ToolContext(), {"value": 1})

    assert result.status == "denied"
    assert "dummy.use" in result.error


@pytest.mark.asyncio
async def test_gateway_executes_with_permission() -> None:
    gateway = ToolGateway()
    gateway.register(DummyTool())

    result = await gateway.execute(
        "dummy", ToolContext(permissions=frozenset({"dummy.use"})), {"value": 1}
    )

    assert result.status == "completed"
    assert result.data == {"value": 1}


@pytest.mark.asyncio
async def test_gateway_rejects_unknown_tool() -> None:
    result = await ToolGateway().execute("missing", ToolContext(), {})

    assert result.status == "error"
    assert result.error == "Unknown tool: missing"


def test_gateway_rejects_duplicate_registration() -> None:
    gateway = ToolGateway()
    gateway.register(DummyTool())

    with pytest.raises(ValueError, match="already registered"):
        gateway.register(DummyTool())


@pytest.mark.asyncio
async def test_web_research_requires_permission() -> None:
    gateway = ToolGateway()
    gateway.register(WebResearchTool())

    result = await gateway.execute("web.research", ToolContext(), {"url": "https://example.com"})

    assert result.status == "denied"
    assert "web.read" in result.error


@pytest.mark.asyncio
async def test_web_research_returns_bounded_text() -> None:
    tool = WebResearchTool()
    tool._validate_url = lambda url: SimpleNamespace(hostname="example.com")
    tool._fetch = lambda url: (b"0123456789", "text/plain")

    result = await tool.execute(
        ToolContext(permissions=frozenset({"web.read"})),
        {"url": "https://example.com", "max_chars": 5},
    )

    assert result.status == "completed"
    assert result.data["text"] == "01234"
