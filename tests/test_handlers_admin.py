"""Integration tests for admin handlers.

Tests status transition via callback + notification to user.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    Chat,
    Message,
    Update,
    User,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from bot.db.repositories import get_booking, upsert_user
from bot.handlers.admin import router as admin_router
from bot.middlewares.db import DbSessionMiddleware
from bot.services.business import BusinessConfig


def _make_user(user_id: int, is_admin: bool = True) -> User:
    return User(id=user_id, is_bot=False, first_name="Admin" if is_admin else "User")


def _make_callback(data: str, user_id: int) -> CallbackQuery:
    msg = MagicMock(spec=Message)
    msg.message_id = 1
    msg.chat = Chat(id=1, type="private")
    msg.from_user = _make_user(user_id)
    msg.edit_text = AsyncMock()
    msg.answer = AsyncMock()
    return CallbackQuery(
        id="cb_id",
        from_user=_make_user(user_id),
        chat_instance="ci",
        data=data,
        message=msg,
    )  # type: ignore[call-arg]


def _build_admin_dp(
    engine: AsyncEngine,
    business_config: BusinessConfig,
    admin_id: int,
) -> tuple[Dispatcher, AsyncMock]:
    bot = AsyncMock()
    bot.id = 42
    bot.send_message = AsyncMock()

    session_pool = async_sessionmaker(engine, expire_on_commit=False)
    dp = Dispatcher(storage=MemoryStorage())
    dp["business"] = business_config
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=session_pool))

    # Patch AdminFilter to allow our admin_id
    import bot.filters as filters_module

    filters_module.settings.admin_ids = [admin_id]  # type: ignore[assignment]

    dp.include_router(admin_router)
    return dp, bot


@pytest.mark.skip(reason="Router single-use in aiogram 3; needs router-factory refactor — TODO")
@pytest.mark.asyncio
async def test_status_transition_persists_and_notifies_user(
    engine: AsyncEngine,
    session: AsyncSession,
    business_config: BusinessConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Admin changes booking status → DB updated + bot.send_message called to user_id."""
    # Setup: create user and booking directly in DB
    user_id = 7001
    admin_id = 9999

    await upsert_user(session, user_id=user_id, full_name="Client", username="client")

    from bot.db.repositories import create_booking

    booking = await create_booking(
        session,
        user_id=user_id,
        service="Медовик",
        client_name="Client",
        phone="+79991234567",
        desired_date="15 июня",
    )

    assert booking.status == "new"

    monkeypatch.setattr("bot.filters.settings.admin_ids", [admin_id])

    dp, bot = _build_admin_dp(engine, business_config, admin_id=admin_id)

    # Admin clicks "confirm" status button: admin:status:<booking_id>:confirmed
    callback_data = f"admin:status:{booking.id}:confirmed"
    cb = _make_callback(callback_data, user_id=admin_id)
    update = Update(update_id=100, callback_query=cb)
    await dp.feed_update(bot, update)

    # Verify: booking status updated in DB
    updated = await get_booking(session, booking.id)
    assert updated is not None
    assert updated.status == "confirmed"

    # Verify: user was notified via bot.send_message
    bot.send_message.assert_called()
    # Notification sent to user's telegram id
    call_args = bot.send_message.call_args_list[0]
    notified_user_id = call_args[0][0]
    assert notified_user_id == user_id
