"""Minimal aiogram test harness.

Wraps Dispatcher.feed_update() with helpers for simulating
Message and CallbackQuery updates using MemoryStorage and AsyncMock Bot.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    Chat,
    Message,
    Update,
    User,
)


def make_fake_bot() -> AsyncMock:
    bot = AsyncMock()
    bot.id = 1
    bot.token = "123456789:fake_token_for_testing"
    bot.send_message = AsyncMock(return_value=MagicMock())
    return bot


def _make_user(user_id: int = 1, username: str = "testuser") -> User:
    return User(
        id=user_id,
        is_bot=False,
        first_name="Test",
        username=username,
    )


def _make_chat(chat_id: int = 1) -> Chat:
    return Chat(id=chat_id, type="private")


def _make_message(
    text: str,
    user_id: int = 1,
    chat_id: int = 1,
    message_id: int = 1,
) -> Message:
    return Message(
        message_id=message_id,
        date=0,
        chat=_make_chat(chat_id),
        from_user=_make_user(user_id),
        text=text,
    )  # type: ignore[call-arg]


def _make_callback(
    data: str,
    user_id: int = 1,
    message_id: int = 1,
) -> CallbackQuery:
    msg = _make_message("", user_id=user_id, message_id=message_id)
    return CallbackQuery(
        id="test_cb",
        from_user=_make_user(user_id),
        chat_instance="test_chat_instance",
        data=data,
        message=msg,
    )  # type: ignore[call-arg]


async def feed_message(
    dp: Dispatcher,
    bot: Any,
    text: str,
    user_id: int = 1,
    chat_id: int = 1,
) -> None:
    msg = _make_message(text, user_id=user_id, chat_id=chat_id)
    update = Update(update_id=1, message=msg)
    await dp.feed_update(bot, update)


async def feed_callback(
    dp: Dispatcher,
    bot: Any,
    data: str,
    user_id: int = 1,
) -> None:
    cb = _make_callback(data, user_id=user_id)
    update = Update(update_id=1, callback_query=cb)
    await dp.feed_update(bot, update)


def make_dispatcher() -> Dispatcher:
    return Dispatcher(storage=MemoryStorage())
