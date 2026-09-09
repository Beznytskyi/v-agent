"""End-to-end tests for the OpenAI-compatible planner boundary."""

from __future__ import annotations

import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from core.orchestrator.protocol import AgentContext
from core.planner.llm import OpenAICompatiblePlannerProvider, PlannerProviderError
from core.planner.service import DeterministicPlannerProvider, Planner


VALID_PLAN = {
    "agent_name": "research",
    "rationale": "Use the research agent for the supplied objective.",
    "steps": [
        {"kind": "agent", "target": "research", "arguments": {}},
        {
            "kind": "tool",
            "target": "web.research",
            "arguments": {"url": "https://example.com"},
        },
    ],
}


def _run(provider: OpenAICompatiblePlannerProvider):
    return asyncio.run(
        provider.plan(
            AgentContext(objective="research the URL", input={"url": "https://example.com"}),
            ["research"],
            ["web.research"],
        )
    )


class _MockHandler(BaseHTTPRequestHandler):
    responses: list[tuple[int, dict]] = []
    delay_seconds = 0.0

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        if self.delay_seconds:
            time.sleep(self.delay_seconds)

        status, payload = self.responses.pop(0)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


def _server(responses, delay_seconds=0.0):
    _MockHandler.responses = list(responses)
    _MockHandler.delay_seconds = delay_seconds
    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _response(plan):
    return {"choices": [{"message": {"content": json.dumps(plan)}}]}


def test_provider_end_to_end_against_mock_openai_endpoint():
    server = _server([(200, _response(VALID_PLAN))])
    try:
        provider = OpenAICompatiblePlannerProvider(
            api_key="test-key",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="test-model",
            max_retries=0,
        )
        plan = _run(provider)
        assert plan.agent_name == "research"
        assert plan.steps[1].target == "web.research"
    finally:
        server.shutdown()
        server.server_close()


def test_provider_retries_transient_http_failure():
    server = _server([(500, {"error": "temporary"}), (200, _response(VALID_PLAN))])
    try:
        provider = OpenAICompatiblePlannerProvider(
            api_key="test-key",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="test-model",
            max_retries=1,
        )
        plan = _run(provider)
        assert plan.agent_name == "research"
        assert _MockHandler.responses == []
    finally:
        server.shutdown()
        server.server_close()


def test_provider_rejects_invalid_structured_output_end_to_end():
    invalid = {
        "agent_name": "research",
        "rationale": "invalid",
        "steps": [{"kind": "tool", "target": "shell.exec", "arguments": {}}],
    }
    server = _server([(200, _response(invalid))])
    try:
        provider = OpenAICompatiblePlannerProvider(
            api_key="test-key",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="test-model",
            max_retries=0,
        )
        with pytest.raises(PlannerProviderError, match="unavailable tool"):
            _run(provider)
    finally:
        server.shutdown()
        server.server_close()


def test_provider_timeout_is_reported_after_retry_budget():
    server = _server([(200, _response(VALID_PLAN)), (200, _response(VALID_PLAN))], delay_seconds=0.15)
    try:
        provider = OpenAICompatiblePlannerProvider(
            api_key="test-key",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="test-model",
            timeout_seconds=0.03,
            max_retries=1,
        )
        with pytest.raises(PlannerProviderError, match="failed after retries"):
            _run(provider)
    finally:
        server.shutdown()
        server.server_close()


def test_deterministic_fallback_remains_default_when_llm_is_disabled(monkeypatch):
    monkeypatch.delenv("V_AGENT_LLM_ENABLED", raising=False)
    planner = Planner()
    assert isinstance(planner.provider, DeterministicPlannerProvider)


def test_llm_is_not_enabled_by_api_key_alone(monkeypatch):
    monkeypatch.delenv("V_AGENT_LLM_ENABLED", raising=False)
    monkeypatch.setenv("V_AGENT_LLM_API_KEY", "present-but-not-enabled")
    planner = Planner()
    assert isinstance(planner.provider, DeterministicPlannerProvider)
