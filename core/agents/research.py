from core.orchestrator.protocol import AgentContext, AgentResult
from core.tools.protocol import ToolContext
from core.tools.registry import ToolRegistry


class ResearchAgent:
    name = "research"

    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools or ToolRegistry.default()

    async def run(self, context: AgentContext) -> AgentResult:
        objective = context.objective.strip()
        findings = [
            {
                "type": "research_request",
                "objective": objective,
                "source": "agent_input",
            }
        ]

        url = str(context.input.get("url", "")).strip()
        if url:
            permissions = frozenset(context.constraints.get("permissions", []))
            tool_result = await self.tools.gateway.execute(
                "web.research",
                ToolContext(permissions=permissions),
                {"url": url, "max_chars": context.input.get("max_chars", 12000)},
            )
            if tool_result.status == "completed":
                findings.append(
                    {
                        "type": "web_source",
                        "url": tool_result.data["url"],
                        "content_type": tool_result.data["content_type"],
                        "text": tool_result.data["text"],
                    }
                )
                return AgentResult(
                    status="completed",
                    summary=f"Research task completed using {url}",
                    findings=findings,
                    recommendations=[],
                )

            if tool_result.status == "denied":
                return AgentResult(
                    status="completed",
                    summary=f"Research task accepted; web access denied for {url}",
                    findings=findings,
                    recommendations=["Grant the web.read permission to fetch the supplied URL."],
                )

            return AgentResult(
                status="completed",
                summary=f"Research task accepted; web retrieval failed for {url}",
                findings=findings,
                recommendations=[tool_result.error or "Web retrieval failed."],
            )

        return AgentResult(
            status="completed",
            summary=f"Research task accepted: {objective}",
            findings=findings,
            recommendations=["Provide input.url to enable the Web Research Tool."],
        )
