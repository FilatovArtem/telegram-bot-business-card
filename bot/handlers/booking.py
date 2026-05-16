import contextlib

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.repositories import create_booking, get_product
from bot.handlers._utils import cb_data, cb_int, cb_message
from bot.keyboards.booking import cancel_kb, confirm_kb
from bot.keyboards.main_menu import back_to_menu_kb
from bot.services.booking import format_booking_notification, validate_phone
from bot.services.messages import Msg

router = Router()

MIN_NAME_LENGTH = 2
MIN_DATE_LENGTH = 3
CONFIRM_WORDS: frozenset[str] = frozenset({"да", "yes", "д", "y"})


class BookingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    confirm = State()


@router.message(Command("cancel"), BookingForm.__all_states__)  # type: ignore[arg-type]  # aiogram accepts State tuples but stubs don't reflect it
async def cmd_cancel_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(Msg.BOOKING_CANCELLED, reply_markup=back_to_menu_kb())


@router.callback_query(F.data == "booking:cancel", StateFilter(BookingForm))
async def cb_cancel_booking(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    msg = cb_message(callback)
    await msg.edit_text(Msg.BOOKING_CANCELLED, reply_markup=back_to_menu_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("order:"))
async def cb_order_product(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    product_id = cb_int(cb_data(callback), 1)
    if product_id is None:
        await callback.answer()
        return
    product = await get_product(session, product_id)
    if product is None:
        await callback.answer(Msg.NOT_FOUND_PRODUCT)
        return

    await state.update_data(service=product.name)
    await cb_message(callback).edit_text(
        f"\U0001f4dd Вы выбрали: <b>{product.name}</b>\n\nВведите ваше имя:",
        reply_markup=cancel_kb(),
    )
    await state.set_state(BookingForm.name)
    await callback.answer()


@router.message(BookingForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < MIN_NAME_LENGTH:
        await message.answer(Msg.NAME_TOO_SHORT, reply_markup=cancel_kb())
        return
    await state.update_data(client_name=name)
    await message.answer(
        "\U0001f4f1 Введите номер телефона (формат: +7XXXXXXXXXX):", reply_markup=cancel_kb()
    )
    await state.set_state(BookingForm.phone)


@router.message(BookingForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if not validate_phone(phone):
        await message.answer(Msg.PHONE_INVALID, reply_markup=cancel_kb())
        return
    await state.update_data(phone=phone)
    await message.answer(
        "\U0001f4c5 Укажите желаемую дату (например: 15 марта, следующая пятница):",
        reply_markup=cancel_kb(),
    )
    await state.set_state(BookingForm.date)


@router.message(BookingForm.date)
async def process_date(message: Message, state: FSMContext) -> None:
    date = (message.text or "").strip()
    if len(date) < MIN_DATE_LENGTH:
        await message.answer(Msg.DATE_TOO_SHORT, reply_markup=cancel_kb())
        return

    await state.update_data(desired_date=date)
    data = await state.get_data()

    summary = (
        f"✅ <b>Подтвердите заявку:</b>\n\n"
        f"\U0001f382 Услуга: {data['service']}\n"
        f"\U0001f464 Имя: {data['client_name']}\n"
        f"\U0001f4f1 Телефон: {data['phone']}\n"
        f"\U0001f4c5 Дата: {data['desired_date']}\n\n"
        f"Все верно? Отправьте <b>Да</b> или <b>Нет</b>."
    )
    await message.answer(summary, reply_markup=confirm_kb())
    await state.set_state(BookingForm.confirm)


@router.callback_query(F.data == "booking:confirm:no", StateFilter(BookingForm))
async def cb_confirm_no(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb_message(callback).edit_text(Msg.BOOKING_CANCELLED, reply_markup=back_to_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "booking:confirm:yes", StateFilter(BookingForm))
async def cb_confirm_yes(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    data = await state.get_data()
    msg = cb_message(callback)
    user_id = callback.from_user.id if callback.from_user else 0

    booking = await create_booking(
        session,
        user_id=user_id,
        service=data["service"],
        client_name=data["client_name"],
        phone=data["phone"],
        desired_date=data["desired_date"],
    )

    await msg.edit_text(
        Msg.BOOKING_ACCEPTED.format(id=booking.id),
        reply_markup=back_to_menu_kb(),
    )

    if settings.admin_chat_id:
        notification = format_booking_notification(
            client_name=data["client_name"],
            phone=data["phone"],
            service=data["service"],
            desired_date=data["desired_date"],
            username=callback.from_user.username if callback.from_user else None,
        )
        with contextlib.suppress(Exception):
            await bot.send_message(settings.admin_chat_id, notification)

    await state.clear()
    await callback.answer()


@router.message(BookingForm.confirm)
async def process_confirm(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    text = (message.text or "").strip().lower()
    if text not in CONFIRM_WORDS:
        await state.clear()
        await message.answer(Msg.BOOKING_CANCELLED, reply_markup=back_to_menu_kb())
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
        Msg.BOOKING_ACCEPTED.format(id=booking.id),
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
