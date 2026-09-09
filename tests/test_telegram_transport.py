import pytest

from apps.telegram.gateway import TelegramGateway
from apps.telegram.transport import TelegramPollingService, parse_text_update


class FakeTelegramApi:
    def __init__(self, updates=None):
        self.calls = []
        self.updates = updates or []

    async def call(self, method, payload):
        self.calls.append((method, payload))
        if method == "getUpdates":
            return {"ok": True, "result": self.updates}
        return {"ok": True, "result": True}


class FakeAgentClient:
    async def run(self, objective):
        return {"status": "completed", "summary": f"done: {objective}"}


@pytest.mark.asyncio
async def test_poll_once_routes_text_message_and_advances_offset():
    api = FakeTelegramApi(
        updates=[
            {
                "update_id": 100,
                "message": {
                    "chat": {"id": 42},
                    "from": {"id": 7},
                    "text": "Проверь статус",
                },
            }
        ]
    )
    gateway = TelegramGateway(FakeAgentClient(), frozenset({7}))
    service = TelegramPollingService(api, gateway, poll_timeout=10)

    processed = await service.poll_once()

    assert processed == 1
    assert api.calls[0] == (
        "getUpdates",
        {"timeout": 10, "allowed_updates": ["message"]},
    )
    assert api.calls[1] == (
        "sendMessage",
        {"chat_id": 42, "text": "[completed]\ndone: Проверь статус"},
    )

    await service.poll_once()
    assert api.calls[2][1]["offset"] == 101


def test_parse_text_update_rejects_non_text_messages():
    assert parse_text_update(
        {
            "update_id": 1,
            "message": {
                "chat": {"id": 42},
                "from": {"id": 7},
                "photo": [],
            },
        }
    ) is None


def test_parse_text_update_extracts_identity_and_chat():
    update = parse_text_update(
        {
            "update_id": 12,
            "message": {
                "chat": {"id": 42},
                "from": {"id": 7},
                "text": "/start",
            },
        }
    )

    assert update is not None
    assert update.update_id == 12
    assert update.chat_id == 42
    assert update.user_id == 7
    assert update.text == "/start"
