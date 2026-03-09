import contextlib

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import (
    count_bookings,
    count_users,
    get_all_user_ids,
    get_booking,
    get_bookings_by_status,
    update_booking_status,
)
from bot.filters import AdminFilter
from bot.keyboards.admin import (
    STATUS_LABELS,
    admin_menu_kb,
    booking_card_kb,
    booking_status_filter_kb,
    bookings_list_kb,
)
from bot.keyboards.main_menu import back_to_menu_kb
from bot.services.booking import format_status_change_notification, format_status_label

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


class BroadcastForm(StatesGroup):
    text = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer("\U0001f527 <b>Админ-панель</b>", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\U0001f527 <b>Админ-панель</b>", reply_markup=admin_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    users = await count_users(session)
    bookings = await count_bookings(session)

    await callback.message.edit_text(  # type: ignore[union-attr]
        f"\U0001f4ca <b>Статистика</b>\n\n\U0001f465 Пользователей: {users}\n\U0001f4cb Заявок: {bookings}",
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()


# ── Booking status management ─────────────────────────────────────


@router.callback_query(F.data == "admin:bookings")
async def cb_booking_statuses(callback: CallbackQuery) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\U0001f4cb <b>Заявки — выберите статус:</b>",
        reply_markup=booking_status_filter_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:bookings:"))
async def cb_bookings_by_status(callback: CallbackQuery, session: AsyncSession) -> None:
    status = callback.data.split(":")[2]  # type: ignore[union-attr]
    bookings = await get_bookings_by_status(session, status)
    label = STATUS_LABELS.get(status, status)

    text = f"{label}\n\nЗаявок нет." if not bookings else f"{label} ({len(bookings)})"

    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=bookings_list_kb(bookings, status)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:booking:"))
async def cb_booking_card(callback: CallbackQuery, session: AsyncSession) -> None:
    booking_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    booking = await get_booking(session, booking_id)
    if booking is None:
        await callback.answer("Заявка не найдена")
        return

    status_label = format_status_label(booking.status)
    text = (
        f"\U0001f4cb <b>Заявка #{booking.id}</b>\n\n"
        f"\U0001f464 {booking.client_name}\n"
        f"\U0001f4f1 {booking.phone}\n"
        f"\U0001f382 {booking.service}\n"
        f"\U0001f4c5 {booking.desired_date}\n"
        f"\U0001f4cb Статус: {status_label}"
    )

    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=booking_card_kb(booking)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:status:"))
async def cb_change_status(callback: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    parts = callback.data.split(":")  # type: ignore[union-attr]
    booking_id = int(parts[2])
    new_status = parts[3]

    booking = await update_booking_status(session, booking_id, new_status)
    if booking is None:
        await callback.answer("Заявка не найдена")
        return

    # Notify user about status change
    notification = format_status_change_notification(booking.id, booking.service, new_status)
    with contextlib.suppress(Exception):
        await bot.send_message(booking.user_id, notification)

    await callback.answer(f"Статус изменён: {format_status_label(new_status)}")

    # Re-render booking card
    status_label = format_status_label(booking.status)
    text = (
        f"\U0001f4cb <b>Заявка #{booking.id}</b>\n\n"
        f"\U0001f464 {booking.client_name}\n"
        f"\U0001f4f1 {booking.phone}\n"
        f"\U0001f382 {booking.service}\n"
        f"\U0001f4c5 {booking.desired_date}\n"
        f"\U0001f4cb Статус: {status_label}"
    )
    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=booking_card_kb(booking)
    )


# ── Broadcast ─────────────────────────────────────────────────────


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\U0001f4e2 Отправьте текст рассылки (или /cancel для отмены):",
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

    user_ids = await get_all_user_ids(session)

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception:  # noqa: BLE001
            failed += 1

    await state.clear()
    await message.answer(
        f"\u2705 Рассылка завершена.\nОтправлено: {sent}\nОшибки: {failed}",
        reply_markup=admin_menu_kb(),
    )
