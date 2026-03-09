from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []
    admin_chat_id: int = 0
    database_url: str = "sqlite+aiosqlite:///data/bot.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: object) -> list[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [int(x) for x in v]
        return []


settings = Settings()  # type: ignore[call-arg]
