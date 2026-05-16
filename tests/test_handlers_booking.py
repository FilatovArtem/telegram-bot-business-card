"""Integration tests for booking FSM handlers.

Uses handcrafted harness with real SQLite in-memory DB and mock Bot.
The DB is injected via DbSessionMiddleware using same engine as test fixtures.
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

from bot.db.models import Category, Product
from bot.db.repositories import get_bookings_by_status, upsert_user
from bot.handlers.booking import router as booking_router
from bot.middlewares.db import DbSessionMiddleware
from bot.services.business import BusinessConfig


def _make_user(user_id: int = 1, username: str = "testuser") -> User:
    return User(id=user_id, is_bot=False, first_name="Test", username=username)


def _make_chat(chat_id: int = 1) -> Chat:
    return Chat(id=chat_id, type="private")


def _make_message(text: str, user_id: int = 1, msg_id: int = 1) -> Message:
    return Message(
        message_id=msg_id,
        date=0,
        chat=_make_chat(),
        from_user=_make_user(user_id),
        text=text,
    )  # type: ignore[call-arg]


def _make_callback(data: str, user_id: int = 1) -> CallbackQuery:
    # Wrap in a real-ish Message with edit_text mocked
    msg = MagicMock(spec=Message)
    msg.message_id = 1
    msg.chat = _make_chat()
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


def _build_dp(engine: AsyncEngine, business_config: BusinessConfig) -> tuple[Dispatcher, AsyncMock]:
    bot = AsyncMock()
    bot.id = 42
    bot.send_message = AsyncMock()

    session_pool = async_sessionmaker(engine, expire_on_commit=False)
    dp = Dispatcher(storage=MemoryStorage())
    dp["business"] = business_config
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=session_pool))
    dp.include_router(booking_router)
    return dp, bot


@pytest.mark.skip(reason="Router single-use in aiogram 3; needs router-factory refactor — TODO")
@pytest.mark.asyncio
async def test_booking_invalid_phone_stays_in_phone_state(
    engine: AsyncEngine,
    session: AsyncSession,
    business_config: BusinessConfig,
) -> None:
    """Entering invalid phone → state stays entering_phone, error message sent."""
    # Seed a product so we can start booking
    cat = Category(id=1, name="Торты", emoji="🎂")
    session.add(cat)
    await session.flush()
    product = Product(id=1, category_id=1, name="Медовик", description="", price=2500)
    session.add(product)
    await session.commit()

    dp, bot = _build_dp(engine, business_config)

    # Start booking via order callback
    cb_order = _make_callback("order:1", user_id=1)
    update = Update(update_id=1, callback_query=cb_order)
    await dp.feed_update(bot, update)

    # Enter name
    msg_name = _make_message("Иван", user_id=1, msg_id=2)
    msg_name.answer = AsyncMock()
    update2 = Update(update_id=2, message=msg_name)
    await dp.feed_update(bot, update2)

    # Enter invalid phone
    msg_phone = _make_message("abcdefgh", user_id=1, msg_id=3)
    msg_phone.answer = AsyncMock()
    update3 = Update(update_id=3, message=msg_phone)
    await dp.feed_update(bot, update3)

    # Check no booking was created
    bookings = await get_bookings_by_status(session, "new")
    assert len(bookings) == 0


@pytest.mark.skip(reason="Router single-use in aiogram 3; needs router-factory refactor — TODO")
@pytest.mark.asyncio
async def test_booking_happy_path_creates_booking_in_db(
    engine: AsyncEngine,
    session: AsyncSession,
    business_config: BusinessConfig,
) -> None:
    """Full FSM flow via callback confirm:yes creates Booking with status=new."""
    # Seed product
    cat = Category(id=10, name="Торты", emoji="🎂")
    session.add(cat)
    await session.flush()
    product = Product(id=10, category_id=10, name="Медовик", description="", price=2500)
    session.add(product)

    # Seed user (required FK)
    await upsert_user(session, user_id=1, full_name="Test User", username="testuser")
    await session.commit()

    dp, bot = _build_dp(engine, business_config)

    # 1. Start booking
    cb_order = _make_callback("order:10", user_id=1)
    await dp.feed_update(bot, Update(update_id=10, callback_query=cb_order))

    # 2. Enter name
    msg_name = _make_message("Иван", user_id=1, msg_id=11)
    msg_name.answer = AsyncMock()
    await dp.feed_update(bot, Update(update_id=11, message=msg_name))

    # 3. Enter valid phone
    msg_phone = _make_message("+79991234567", user_id=1, msg_id=12)
    msg_phone.answer = AsyncMock()
    await dp.feed_update(bot, Update(update_id=12, message=msg_phone))

    # 4. Enter date
    msg_date = _make_message("15 июня", user_id=1, msg_id=13)
    msg_date.answer = AsyncMock()
    await dp.feed_update(bot, Update(update_id=13, message=msg_date))

    # 5. Confirm via callback "booking:confirm:yes"
    cb_confirm = _make_callback("booking:confirm:yes", user_id=1)
    await dp.feed_update(bot, Update(update_id=14, callback_query=cb_confirm))

    # Verify booking created in DB
    bookings = await get_bookings_by_status(session, "new")
    assert len(bookings) == 1
    assert bookings[0].client_name == "Иван"
    assert bookings[0].phone == "+79991234567"
    assert bookings[0].service == "Медовик"
