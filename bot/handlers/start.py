from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import upsert_user
from bot.keyboards.main_menu import back_to_menu_kb, main_menu_kb
from bot.services.business import BusinessConfig

router = Router()


def _biz(bot: Bot) -> BusinessConfig:
    return bot["business"]


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot) -> None:
    if message.from_user:
        await upsert_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    await message.answer(_biz(bot).welcome_html(), reply_markup=main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, bot: Bot) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        _biz(bot).welcome_html(), reply_markup=main_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery, bot: Bot) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        _biz(bot).about_html(), reply_markup=back_to_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def cb_contacts(callback: CallbackQuery, bot: Bot) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        _biz(bot).contacts_html(), reply_markup=back_to_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()
