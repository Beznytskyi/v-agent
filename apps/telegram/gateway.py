from dataclasses import dataclass
from typing import Any, Protocol


class AgentRunClient(Protocol):
    async def run(self, objective: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class TelegramMessage:
    chat_id: int
    user_id: int
    text: str


class UnauthorizedTelegramUser(Exception):
    pass


class TelegramGateway:
    """Channel adapter: Telegram messages in, V-Agent results out."""

    def __init__(self, client: AgentRunClient, allowed_user_ids: frozenset[int]) -> None:
        self.client = client
        self.allowed_user_ids = allowed_user_ids

    def authorize(self, user_id: int) -> None:
        if user_id not in self.allowed_user_ids:
            raise UnauthorizedTelegramUser("Telegram user is not authorized")

    async def handle(self, message: TelegramMessage) -> str:
        self.authorize(message.user_id)
        text = message.text.strip()
        if not text:
            return "Пожалуйста, напишите задачу."

        if text == "/start":
            return "V-Agent подключён. Напишите задачу, которую нужно выполнить."
        if text == "/help":
            return "Команды: /start, /help, /new. Обычное сообщение — задача для V-Agent."
        if text == "/new":
            return "Новая задача. Напишите, что нужно сделать."

        result = await self.client.run(text)
        return format_agent_result(result)


def format_agent_result(result: dict[str, Any]) -> str:
    status = str(result.get("status", "completed"))
    summary = str(result.get("summary", "")).strip()
    if summary:
        return f"[{status}]\n{summary}"
    return f"[{status}] Задача обработана."
