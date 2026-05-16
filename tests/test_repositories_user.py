import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import count_users, get_all_user_ids, upsert_user


@pytest.mark.asyncio
async def test_upsert_creates_new_user(session: AsyncSession) -> None:
    user = await upsert_user(session, user_id=1001, full_name="Иван Иванов", username="ivan")

    assert user.id == 1001
    assert user.full_name == "Иван Иванов"
    assert user.username == "ivan"
    assert await count_users(session) == 1


@pytest.mark.asyncio
async def test_upsert_updates_existing_user_name(session: AsyncSession) -> None:
    await upsert_user(session, user_id=1002, full_name="Старое Имя", username="user1")
    updated = await upsert_user(session, user_id=1002, full_name="Новое Имя", username="user_new")

    assert updated.id == 1002
    assert updated.full_name == "Новое Имя"
    assert updated.username == "user_new"
    # Count must stay 1 — no duplicates
    assert await count_users(session) == 1


@pytest.mark.asyncio
async def test_get_all_user_ids_returns_int_list(session: AsyncSession) -> None:
    await upsert_user(session, user_id=2001, full_name="User A", username=None)
    await upsert_user(session, user_id=2002, full_name="User B", username="user_b")

    ids = await get_all_user_ids(session)

    assert isinstance(ids, list)
    assert 2001 in ids
    assert 2002 in ids
    assert all(isinstance(i, int) for i in ids)
