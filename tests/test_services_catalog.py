from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Category
from bot.services.catalog import seed_catalog


@pytest.mark.asyncio
async def test_seed_empty_db_loads_json(session: AsyncSession, seed_json: Path) -> None:
    await seed_catalog(session, seed_path=str(seed_json))

    result = await session.execute(select(Category))
    categories = list(result.scalars().all())
    assert len(categories) == 1
    assert categories[0].name == "Cat"


@pytest.mark.asyncio
async def test_seed_idempotent_if_already_seeded(session: AsyncSession, seed_json: Path) -> None:
    # Seed once
    await seed_catalog(session, seed_path=str(seed_json))

    # Seed again — must be no-op
    await seed_catalog(session, seed_path=str(seed_json))

    result = await session.execute(select(Category))
    categories = list(result.scalars().all())
    assert len(categories) == 1  # still 1, not 2


@pytest.mark.asyncio
async def test_seed_missing_file_is_noop(session: AsyncSession) -> None:
    # Does not raise, DB stays empty
    await seed_catalog(session, seed_path="/nonexistent/seed.json")

    result = await session.execute(select(Category))
    categories = list(result.scalars().all())
    assert len(categories) == 0


@pytest.mark.asyncio
async def test_seed_malformed_json_is_noop(session: AsyncSession, tmp_path: Path) -> None:
    bad_file = tmp_path / "seed.json"
    bad_file.write_text("{broken json", encoding="utf-8")

    # Does not raise, DB stays empty
    await seed_catalog(session, seed_path=str(bad_file))

    result = await session.execute(select(Category))
    categories = list(result.scalars().all())
    assert len(categories) == 0
