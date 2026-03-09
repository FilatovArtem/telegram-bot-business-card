import contextlib

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.repositories import create_booking, get_product
from bot.keyboards.main_menu import back_to_menu_kb
from bot.services.booking import format_booking_notification, validate_phone

router = Router()


class BookingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    confirm = State()


@router.message(Command("cancel"), BookingForm.__all_states__)
async def cmd_cancel_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("\u274c Заявка отменена.", reply_markup=back_to_menu_kb())


@router.callback_query(F.data.startswith("order:"))
async def cb_order_product(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    product_id = int(callback.data.split(":")[1])  # type: ignore[union-attr]
    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("Товар не найден")
        return

    await state.update_data(service=product.name)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"\U0001f4dd Вы выбрали: <b>{product.name}</b>\n\nВведите ваше имя:",
    )
    await state.set_state(BookingForm.name)
    await callback.answer()


@router.message(BookingForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Попробуйте еще раз:")
        return
    await state.update_data(client_name=name)
    await message.answer("\U0001f4f1 Введите номер телефона (формат: +7XXXXXXXXXX):")
    await state.set_state(BookingForm.phone)


@router.message(BookingForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if not validate_phone(phone):
        await message.answer("\u274c Неверный формат телефона.\nВведите в формате: +7 (XXX) XXX-XX-XX")
        return
    await state.update_data(phone=phone)
    await message.answer("\U0001f4c5 Укажите желаемую дату (например: 15 марта, следующая пятница):")
    await state.set_state(BookingForm.date)


@router.message(BookingForm.date)
async def process_date(message: Message, state: FSMContext) -> None:
    date = (message.text or "").strip()
    if len(date) < 3:
        await message.answer("Уточните дату, пожалуйста:")
        return

    await state.update_data(desired_date=date)
    data = await state.get_data()

    summary = (
        f"\u2705 <b>Подтвердите заявку:</b>\n\n"
        f"\U0001f382 Услуга: {data['service']}\n"
        f"\U0001f464 Имя: {data['client_name']}\n"
        f"\U0001f4f1 Телефон: {data['phone']}\n"
        f"\U0001f4c5 Дата: {data['desired_date']}\n\n"
        f"Все верно? Отправьте <b>Да</b> или <b>Нет</b>."
    )
    await message.answer(summary)
    await state.set_state(BookingForm.confirm)


@router.message(BookingForm.confirm)
async def process_confirm(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    text = (message.text or "").strip().lower()
    if text not in ("да", "yes", "д", "y"):
        await state.clear()
        await message.answer("\u274c Заявка отменена.", reply_markup=back_to_menu_kb())
        return

    data = await state.get_data()
    user_id = message.from_user.id if message.from_user else 0

    booking = await create_booking(
        session,
        user_id=user_id,
        service=data["service"],
        client_name=data["client_name"],
        phone=data["phone"],
        desired_date=data["desired_date"],
    )

    await message.answer(
        f"\u2705 <b>Заявка #{booking.id} принята!</b>\nМы свяжемся с вами для подтверждения.",
        reply_markup=back_to_menu_kb(),
    )

    if settings.admin_chat_id:
        notification = format_booking_notification(
            client_name=data["client_name"],
            phone=data["phone"],
            service=data["service"],
            desired_date=data["desired_date"],
            username=message.from_user.username if message.from_user else None,
        )
        with contextlib.suppress(Exception):
            await bot.send_message(settings.admin_chat_id, notification)

    await state.clear()
