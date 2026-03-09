import contextlib

from aiogram import Bot, F, Router
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
    service = State()
    name = State()
    phone = State()
    date = State()
    confirm = State()


SERVICES = [
    "Торт на заказ",
    "Набор пирожных",
    "Капкейки на праздник",
    "Десертный стол",
]


@router.callback_query(F.data == "booking")
async def cb_booking_start(callback: CallbackQuery, state: FSMContext) -> None:
    services_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(SERVICES))
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📝 <b>Запись на заказ</b>\n\n"
        f"Выберите услугу (отправьте номер):\n{services_text}",
        parse_mode="HTML",
    )
    await state.set_state(BookingForm.service)
    await callback.answer()


@router.callback_query(F.data.startswith("order:"))
async def cb_order_product(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    product_id = int(callback.data.split(":")[1])  # type: ignore[union-attr]
    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("Товар не найден")
        return

    await state.update_data(service=product.name)
    await callback.message.edit_text(  # type: ignore[union-attr]
        f"📝 Вы выбрали: <b>{product.name}</b>\n\nВведите ваше имя:",
        parse_mode="HTML",
    )
    await state.set_state(BookingForm.name)
    await callback.answer()


@router.message(BookingForm.service)
async def process_service(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    if text.isdigit() and 1 <= int(text) <= len(SERVICES):  # noqa: SIM108
        service = SERVICES[int(text) - 1]
    else:
        service = text.strip()

    await state.update_data(service=service)
    await message.answer("👤 Введите ваше имя:")
    await state.set_state(BookingForm.name)


@router.message(BookingForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Попробуйте еще раз:")
        return
    await state.update_data(client_name=name)
    await message.answer("📱 Введите номер телефона (формат: +7XXXXXXXXXX):")
    await state.set_state(BookingForm.phone)


@router.message(BookingForm.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if not validate_phone(phone):
        await message.answer(
            "❌ Неверный формат телефона.\n"
            "Введите в формате: +7 (XXX) XXX-XX-XX"
        )
        return
    await state.update_data(phone=phone)
    await message.answer("📅 Укажите желаемую дату (например: 15 марта, следующая пятница):")
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
        f"✅ <b>Подтвердите заявку:</b>\n\n"
        f"🎂 Услуга: {data['service']}\n"
        f"👤 Имя: {data['client_name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"📅 Дата: {data['desired_date']}\n\n"
        f"Все верно? Отправьте <b>Да</b> или <b>Нет</b>."
    )
    await message.answer(summary, parse_mode="HTML")
    await state.set_state(BookingForm.confirm)


@router.message(BookingForm.confirm)
async def process_confirm(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    text = (message.text or "").strip().lower()
    if text not in ("да", "yes", "д", "y"):
        await state.clear()
        await message.answer(
            "❌ Заявка отменена.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML",
        )
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
        f"✅ <b>Заявка #{booking.id} принята!</b>\n"
        f"Мы свяжемся с вами для подтверждения.",
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML",
    )

    # Notify admin
    if settings.admin_chat_id:
        notification = format_booking_notification(
            client_name=data["client_name"],
            phone=data["phone"],
            service=data["service"],
            desired_date=data["desired_date"],
            username=message.from_user.username if message.from_user else None,
        )
        with contextlib.suppress(Exception):
            await bot.send_message(
                settings.admin_chat_id, notification, parse_mode="HTML"
            )

    await state.clear()
