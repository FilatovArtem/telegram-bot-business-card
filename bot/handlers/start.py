from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import upsert_user
from bot.keyboards.main_menu import back_to_menu_kb, main_menu_kb

router = Router()

WELCOME = (
    "🍰 <b>Добро пожаловать в SweetDream!</b>\n\n"
    "Домашняя кондитерская с авторскими десертами.\n"
    "Выберите, что вас интересует:"
)

ABOUT = (
    "🏠 <b>О нас</b>\n\n"
    "SweetDream - домашняя кондитерская в Москве.\n"
    "Готовим торты, пирожные и капкейки из натуральных ингредиентов.\n"
    "Работаем с 2020 года. Более 500 довольных клиентов."
)

CONTACTS = (
    "📞 <b>Контакты</b>\n\n"
    "📱 Телефон: +7 (999) 123-45-67\n"
    "📧 Email: hello@sweetdream.ru\n"
    "📍 Москва, ул. Примерная, д. 1\n"
    "🕐 Прием заказов: 9:00 - 21:00"
)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if message.from_user:
        await upsert_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    await message.answer(WELCOME, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        WELCOME, reply_markup=main_menu_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        ABOUT, reply_markup=back_to_menu_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def cb_contacts(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        CONTACTS, reply_markup=back_to_menu_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()
