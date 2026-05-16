import logging

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, ErrorEvent, Message

from bot.config import settings
from bot.services.messages import Msg

logger = logging.getLogger(__name__)


def register_error_handler(dp: Dispatcher, bot: Bot) -> None:
    @dp.error()
    async def handle_all_errors(event: ErrorEvent) -> bool:
        update = event.update
        exc = event.exception

        logger.exception(
            "Unhandled error in update %s",
            update.update_id,
            exc_info=exc,
        )

        # Reply to user if possible
        if update.message is not None and isinstance(update.message, Message):
            try:
                await update.message.answer(Msg.GENERIC_ERROR)
            except Exception:
                logger.exception("Failed to send error message to user")
        elif update.callback_query is not None and isinstance(update.callback_query, CallbackQuery):
            try:
                await update.callback_query.answer(Msg.GENERIC_ERROR, show_alert=True)
            except Exception:
                logger.exception("Failed to answer callback query on error")

        # Notify admin chat
        if settings.admin_chat_id:
            try:
                await bot.send_message(
                    settings.admin_chat_id,
                    f"⚠️ Bot error\n"
                    f"<code>update_id={update.update_id}</code>\n"
                    f"<code>{type(exc).__name__}: {exc}</code>",
                )
            except Exception:
                logger.exception("Failed to notify admin chat about error")

        return True
