from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import upsert_user
from bot.handlers._utils import cb_message
from bot.keyboards.main_menu import back_to_menu_kb, main_menu_kb
from bot.services.business import BusinessConfig
from bot.services.messages import Msg

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message, session: AsyncSession, business: BusinessConfig, state: FSMContext
) -> None:
    await state.clear()
    if message.from_user:
        await upsert_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    await message.answer(business.welcome_html(), reply_markup=main_menu_kb())


@router.message(Command("cancel"))
async def cmd_cancel_global(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(Msg.CANCEL_AND_RETURN, reply_markup=main_menu_kb())


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, business: BusinessConfig) -> None:
    await cb_message(callback).edit_text(business.welcome_html(), reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery, business: BusinessConfig) -> None:
    await cb_message(callback).edit_text(business.about_html(), reply_markup=back_to_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def cb_contacts(callback: CallbackQuery, business: BusinessConfig) -> None:
    await cb_message(callback).edit_text(business.contacts_html(), reply_markup=back_to_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()
