import asyncio
import ipaddress
import socket
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from core.tools.protocol import Tool, ToolContext, ToolResult, ToolSpec


class WebResearchTool(Tool):
    """Read public HTTP(S) pages through a permission-gated tool boundary."""

    spec = ToolSpec(
        name="web.research",
        description="Fetch a public web page and return a bounded text snapshot.",
        risk_level="low",
        permissions=frozenset({"web.read"}),
    )

    def __init__(self, timeout: float = 10.0, max_bytes: int = 1_000_000) -> None:
        self.timeout = timeout
        self.max_bytes = max_bytes

    async def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        url = str(arguments.get("url", "")).strip()
        if not url:
            return ToolResult(status="error", error="url is required")

        try:
            parsed = self._validate_url(url)
            body, content_type = await asyncio.to_thread(self._fetch, url)
            text = body.decode("utf-8", errors="replace")
            return ToolResult(
                status="completed",
                data={
                    "url": url,
                    "host": parsed.hostname,
                    "content_type": content_type,
                    "text": text[: int(arguments.get("max_chars", 12000))],
                },
            )
        except (ValueError, OSError, UnicodeError) as exc:
            return ToolResult(status="error", error=str(exc))

    def _validate_url(self, url: str):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed")
        if not parsed.hostname:
            raise ValueError("URL host is required")
        if parsed.username or parsed.password:
            raise ValueError("Credentials in URLs are not allowed")

        addresses = socket.getaddrinfo(parsed.hostname, None, type=socket.SOCK_STREAM)
        for _, _, _, _, sockaddr in addresses:
            address = ipaddress.ip_address(sockaddr[0])
            if not address.is_global:
                raise ValueError("Private or non-global network targets are blocked")
        return parsed

    def _fetch(self, url: str) -> tuple[bytes, str]:
        request = Request(
            url,
            headers={"User-Agent": "V-Agent/0.5 (+https://github.com/Beznytskyi/v-agent)"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith(("text/", "application/json", "application/xml")):
                raise ValueError(f"Unsupported content type: {content_type}")
            body = response.read(self.max_bytes + 1)
            if len(body) > self.max_bytes:
                raise ValueError("Response exceeds configured size limit")
            return body, content_type
