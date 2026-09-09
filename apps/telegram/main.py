from __future__ import annotations

import asyncio
import os

from apps.telegram.client import VAgentApiClient
from apps.telegram.config import load_config, validate_config
from apps.telegram.gateway import TelegramGateway
from apps.telegram.transport import TelegramBotApi, TelegramPollingService


def _load_api_base_url() -> str:
    return os.getenv("V_AGENT_API_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")


def build_service() -> TelegramPollingService:
    config = load_config()
    validate_config(config)
    if not config.enabled:
        raise RuntimeError("Telegram integration is disabled")

    api = TelegramBotApi(config.bot_token)
    client = VAgentApiClient(base_url=_load_api_base_url())
    gateway = TelegramGateway(client, config.allowed_user_ids)
    return TelegramPollingService(api, gateway)


async def main() -> None:
    service = build_service()
    try:
        await service.run_forever()
    except KeyboardInterrupt:
        service.stop()


if __name__ == "__main__":
    asyncio.run(main())
