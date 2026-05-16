"""Tests for global error handler registered via register_error_handler().

Strategy: extract registered handler from dp.errors.handlers directly
and call it with a mock ErrorEvent. Avoids full dispatch pipeline complexity.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Update

from bot.handlers.errors import register_error_handler


def _make_error_event(exception: Exception, update_id: int = 1) -> ErrorEvent:
    update = MagicMock(spec=Update)
    update.update_id = update_id
    update.message = None
    update.callback_query = None
    return ErrorEvent(update=update, exception=exception)


@pytest.mark.asyncio
async def test_error_handler_notifies_admin_when_admin_chat_set() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    bot = AsyncMock()
    bot.send_message = AsyncMock()

    with patch("bot.handlers.errors.settings") as mock_settings:
        mock_settings.admin_chat_id = 12345

        register_error_handler(dp, bot)

        # Find and invoke the registered error handler
        handlers = dp.errors.handlers
        assert len(handlers) > 0

        error_event = _make_error_event(ValueError("Test error"))

        # Call handler directly (it returns True)
        handler_callable = handlers[0].callback
        result = await handler_callable(error_event)

    assert result is True
    # Admin should be notified
    bot.send_message.assert_called_once()
    call_kwargs = bot.send_message.call_args
    assert call_kwargs[0][0] == 12345  # sent to admin_chat_id
    # Message text contains exception info
    sent_text = call_kwargs[0][1]
    assert "ValueError" in sent_text


@pytest.mark.asyncio
async def test_error_handler_does_not_crash_when_no_admin_chat() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    bot = AsyncMock()
    bot.send_message = AsyncMock()

    with patch("bot.handlers.errors.settings") as mock_settings:
        mock_settings.admin_chat_id = 0  # disabled

        register_error_handler(dp, bot)

        handlers = dp.errors.handlers
        assert len(handlers) > 0

        error_event = _make_error_event(RuntimeError("Some error"))
        handler_callable = handlers[0].callback
        result = await handler_callable(error_event)

    assert result is True
    # Must NOT call send_message when admin_chat_id == 0
    bot.send_message.assert_not_called()
