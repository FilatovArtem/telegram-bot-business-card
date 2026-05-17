import sys

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []
    admin_chat_id: int = 0
    database_url: str = "sqlite+aiosqlite:///data/bot.db"
    # Optional HTTP(S)/SOCKS proxy for outbound Telegram API requests.
    # Use when the host network blocks api.telegram.org directly.
    # Example: http://127.0.0.1:10808 (host xray/v2ray HTTP inbound).
    bot_proxy: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        if not v or len(v) < 20 or ":" not in v:
            raise ValueError("BOT_TOKEN invalid (expected: <digits>:<alphanumeric>, min 20 chars)")
        return v

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: object) -> list[int]:
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            ids = [int(x.strip()) for x in v.split(",") if x.strip()]
            if not ids:
                raise ValueError("ADMIN_IDS must contain at least one admin user ID")
            return ids
        if isinstance(v, list):
            result = [int(x) for x in v]
            if not result:
                raise ValueError("ADMIN_IDS must contain at least one admin user ID")
            return result
        raise ValueError("ADMIN_IDS must contain at least one admin user ID")


try:
    # pydantic-settings loads from env at runtime; call-arg is populated via model_config
    settings = Settings()  # type: ignore[call-arg]
except ValueError as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    raise SystemExit(1) from e
