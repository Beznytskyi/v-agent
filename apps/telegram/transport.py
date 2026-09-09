from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from apps.telegram.gateway import TelegramGateway, TelegramMessage, UnauthorizedTelegramUser


class TelegramTransportError(RuntimeError):
    """Raised when the Telegram Bot API cannot be reached or rejects a request."""


class TelegramApi(Protocol):
    async def call(self, method: str, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class TelegramUpdate:
    update_id: int
    chat_id: int
    user_id: int
    text: str


def _post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise TelegramTransportError("Telegram Bot API request failed") from exc

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TelegramTransportError("Telegram Bot API returned invalid JSON") from exc

    if not isinstance(result, dict) or result.get("ok") is not True:
        description = result.get("description", "unknown Telegram API error") if isinstance(result, dict) else "invalid response"
        raise TelegramTransportError(str(description))
    return result


class TelegramBotApi:
    def __init__(self, bot_token: str, timeout: float = 35.0) -> None:
        if not bot_token:
            raise ValueError("bot_token is required")
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
        self._timeout = timeout

    async def call(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await asyncio.to_thread(
            _post_json,
            f"{self._base_url}/{method}",
            payload,
            self._timeout,
        )


class TelegramPollingService:
    """Long-poll Telegram updates and route text messages through TelegramGateway."""

    def __init__(
        self,
        api: TelegramApi,
        gateway: TelegramGateway,
        poll_timeout: int = 30,
    ) -> None:
        if poll_timeout < 0 or poll_timeout > 50:
            raise ValueError("poll_timeout must be between 0 and 50 seconds")
        self.api = api
        self.gateway = gateway
        self.poll_timeout = poll_timeout
        self._offset: int | None = None
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    async def poll_once(self) -> int:
        payload: dict[str, Any] = {
            "timeout": self.poll_timeout,
            "allowed_updates": ["message"],
        }
        if self._offset is not None:
            payload["offset"] = self._offset

        result = await self.api.call("getUpdates", payload)
        updates = result.get("result", [])
        if not isinstance(updates, list):
            raise TelegramTransportError("Telegram getUpdates returned an invalid result")

        processed = 0
        for update in updates:
            parsed = parse_text_update(update)
            update_id = update.get("update_id") if isinstance(update, dict) else None
            if not isinstance(update_id, int):
                continue
            self._offset = update_id + 1
            if parsed is None:
                continue
            await self._handle_message(parsed)
            processed += 1
        return processed

    async def _handle_message(self, message: TelegramUpdate) -> None:
        try:
            response = await self.gateway.handle(
                TelegramMessage(
                    chat_id=message.chat_id,
                    user_id=message.user_id,
                    text=message.text,
                )
            )
        except UnauthorizedTelegramUser:
            return
        except Exception:
            # Do not leak internal exception details or credentials to Telegram.
            response = "Не удалось обработать задачу. Попробуйте ещё раз."

        await self.api.call(
            "sendMessage",
            {"chat_id": message.chat_id, "text": response},
        )

    async def run_forever(self, retry_delay: float = 2.0) -> None:
        while not self._stopped:
            try:
                await self.poll_once()
            except TelegramTransportError:
                if self._stopped:
                    break
                await asyncio.sleep(retry_delay)


def parse_text_update(update: dict[str, Any]) -> TelegramUpdate | None:
    message = update.get("message")
    if not isinstance(message, dict):
        return None
    chat = message.get("chat")
    user = message.get("from")
    text = message.get("text")
    update_id = update.get("update_id")
    chat_id = chat.get("id") if isinstance(chat, dict) else None
    user_id = user.get("id") if isinstance(user, dict) else None
    if not all(isinstance(value, int) for value in (update_id, chat_id, user_id)):
        return None
    if not isinstance(text, str):
        return None
    return TelegramUpdate(
        update_id=update_id,
        chat_id=chat_id,
        user_id=user_id,
        text=text,
    )
