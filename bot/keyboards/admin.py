from aiogram.types import InlineKeyboardButton as Btn
from aiogram.types import InlineKeyboardMarkup

from bot.db.models import Booking, BookingStatus

STATUS_LABELS: dict[str, str] = {
    BookingStatus.NEW: "\U0001f195 Новые",
    BookingStatus.CONFIRMED: "\u2705 Подтверждённые",
    BookingStatus.COMPLETED: "\u2705 Завершённые",
    BookingStatus.CANCELLED: "\u274c Отменённые",
}

STATUS_EMOJI: dict[str, str] = {
    BookingStatus.NEW: "\U0001f195",
    BookingStatus.CONFIRMED: "\u2705",
    BookingStatus.COMPLETED: "\u2714\ufe0f",
    BookingStatus.CANCELLED: "\u274c",
}


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [Btn(text="\U0001f4ca Статистика", callback_data="admin:stats")],
            [Btn(text="\U0001f4cb Заявки", callback_data="admin:bookings")],
            [Btn(text="\U0001f4e2 Рассылка", callback_data="admin:broadcast")],
            [Btn(text="\u2b05\ufe0f Меню", callback_data="main_menu")],
        ]
    )


def booking_status_filter_kb() -> InlineKeyboardMarkup:
    buttons = [
        [Btn(text=label, callback_data=f"admin:bookings:{status}")] for status, label in STATUS_LABELS.items()
    ]
    buttons.append([Btn(text="\u2b05\ufe0f Админ-панель", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bookings_list_kb(bookings: list[Booking], status: str) -> InlineKeyboardMarkup:
    buttons = [
        [Btn(text=f"#{b.id} {b.client_name} — {b.service}", callback_data=f"admin:booking:{b.id}")]
        for b in bookings
    ]
    buttons.append([Btn(text="\u2b05\ufe0f Статусы", callback_data="admin:bookings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def booking_card_kb(booking: Booking) -> InlineKeyboardMarkup:
    transitions: dict[str, list[str]] = {
        BookingStatus.NEW: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
        BookingStatus.CONFIRMED: [BookingStatus.COMPLETED, BookingStatus.CANCELLED],
        BookingStatus.COMPLETED: [],
        BookingStatus.CANCELLED: [],
    }
    buttons = [
        [
            Btn(
                text=f"{STATUS_EMOJI[s]} {STATUS_LABELS[s].split(' ', 1)[1]}",
                callback_data=f"admin:status:{booking.id}:{s}",
            )
        ]
        for s in transitions.get(booking.status, [])
    ]
    buttons.append([Btn(text="\u2b05\ufe0f Назад", callback_data=f"admin:bookings:{booking.status}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
