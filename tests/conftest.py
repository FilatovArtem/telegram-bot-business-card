from __future__ import annotations

import os

# Must be set before any bot.* imports — bot/config.py runs Settings() at module level.
# Without a valid token the module raises SystemExit and collection fails.
# Use assignment (not setdefault) to override values from local .env that may be invalid.
os.environ["BOT_TOKEN"] = "123456789:AABBCCDDEEFFaabbccddeeff_test_token"
os.environ["ADMIN_IDS"] = "999"

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.db.models import Base
from bot.services.business import BusinessConfig, ContactsConfig


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as s:
        yield s


@pytest.fixture
def business_config() -> BusinessConfig:
    return BusinessConfig(
        name="TestBiz",
        welcome="welcome",
        about="about",
        contacts=ContactsConfig(
            phone="+79991234567",
            email="test@test.ru",
            address="addr",
            hours="9-18",
        ),
    )


@pytest.fixture
def seed_json(tmp_path: Path) -> Path:
    path = tmp_path / "seed.json"
    path.write_text(
        '{"categories":[{"id":1,"name":"Cat","emoji":"X",'
        '"products":[{"name":"P","description":"","price":100}]}]}',
        encoding="utf-8",
    )
    return path
