import pytest

from apps.telegram.gateway import (
    TelegramGateway,
    TelegramMessage,
    UnauthorizedTelegramUser,
)


class FakeAgentRunClient:
    def __init__(self, result: dict):
        self.result = result
        self.objectives: list[str] = []

    async def run(self, objective: str) -> dict:
        self.objectives.append(objective)
        return self.result


@pytest.mark.asyncio
async def test_telegram_message_is_forwarded_to_agent():
    client = FakeAgentRunClient({"status": "completed", "summary": "Готово"})
    gateway = TelegramGateway(client, frozenset({123}))

    response = await gateway.handle(TelegramMessage(10, 123, "Проверь задачу"))

    assert response == "[completed]\nГотово"
    assert client.objectives == ["Проверь задачу"]


@pytest.mark.asyncio
async def test_unauthorized_user_is_rejected():
    gateway = TelegramGateway(FakeAgentRunClient({}), frozenset({123}))

    with pytest.raises(UnauthorizedTelegramUser):
        await gateway.handle(TelegramMessage(10, 999, "Секретная задача"))


@pytest.mark.asyncio
async def test_commands_are_handled_without_agent_call():
    client = FakeAgentRunClient({"status": "completed", "summary": "unexpected"})
    gateway = TelegramGateway(client, frozenset({123}))

    assert "V-Agent подключён" in await gateway.handle(TelegramMessage(10, 123, "/start"))
    assert "Команды" in await gateway.handle(TelegramMessage(10, 123, "/help"))
    assert "Новая задача" in await gateway.handle(TelegramMessage(10, 123, "/new"))
    assert client.objectives == []


@pytest.mark.asyncio
async def test_empty_message_does_not_call_agent():
    client = FakeAgentRunClient({})
    gateway = TelegramGateway(client, frozenset({123}))

    assert await gateway.handle(TelegramMessage(10, 123, "   ")) == "Пожалуйста, напишите задачу."
    assert client.objectives == []
