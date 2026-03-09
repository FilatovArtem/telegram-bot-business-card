from aiogram import Bot, F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.models import User
from bot.db.repositories import count_bookings, count_users, get_recent_bookings
from bot.keyboards.admin import admin_menu_kb
from bot.keyboards.main_menu import back_to_menu_kb


class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user is not None and event.from_user.id in settings.admin_ids


router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


class BroadcastForm(StatesGroup):
    text = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer(
        "🔧 <b>Админ-панель</b>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    users = await count_users(session)
    bookings = await count_bookings(session)

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📊 <b>Статистика</b>\n\n👥 Пользователей: {users}\n📋 Заявок: {bookings}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:bookings")
async def cb_admin_bookings(callback: CallbackQuery, session: AsyncSession) -> None:
    bookings = await get_recent_bookings(session, limit=10)
    if not bookings:
        text = "📋 Заявок пока нет."
    else:
        lines = []
        for b in bookings:
            lines.append(f"<b>#{b.id}</b> | {b.client_name} | {b.phone}\n    {b.service} | {b.desired_date}")
        text = "📋 <b>Последние заявки:</b>\n\n" + "\n\n".join(lines)

    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=admin_menu_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📢 Отправьте текст рассылки (или /cancel для отмены):",
        parse_mode="HTML",
    )
    await state.set_state(BroadcastForm.text)
    await callback.answer()


@router.message(BroadcastForm.text)
async def process_broadcast(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    text = message.text or ""
    if text == "/cancel":
        await state.clear()
        await message.answer("Рассылка отменена.", reply_markup=back_to_menu_kb())
        return

    result = await session.execute(select(User.id))
    user_ids = [row[0] for row in result.all()]

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
        except Exception:  # noqa: BLE001
            failed += 1

    await state.clear()
    await message.answer(
        f"✅ Рассылка завершена.\nОтправлено: {sent}\nОшибки: {failed}",
        reply_markup=admin_menu_kb(),
    )
