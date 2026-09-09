from dataclasses import dataclass
import os


@dataclass(frozen=True)
class TelegramConfig:
    enabled: bool
    bot_token: str
    allowed_user_ids: frozenset[int]


def _parse_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_user_ids(value: str | None) -> frozenset[int]:
    ids: set[int] = set()
    for item in (value or "").split(","):
        item = item.strip()
        if item:
            ids.add(int(item))
    return frozenset(ids)


def load_config() -> TelegramConfig:
    return TelegramConfig(
        enabled=_parse_bool(os.getenv("V_AGENT_TELEGRAM_ENABLED")),
        bot_token=os.getenv("V_AGENT_TELEGRAM_BOT_TOKEN", "").strip(),
        allowed_user_ids=_parse_user_ids(os.getenv("V_AGENT_TELEGRAM_ALLOWED_USER_IDS")),
    )


def validate_config(config: TelegramConfig) -> None:
    if not config.enabled:
        return
    if not config.bot_token:
        raise ValueError("V_AGENT_TELEGRAM_BOT_TOKEN is required when Telegram is enabled")
    if not config.allowed_user_ids:
        raise ValueError("V_AGENT_TELEGRAM_ALLOWED_USER_IDS is required when Telegram is enabled")
