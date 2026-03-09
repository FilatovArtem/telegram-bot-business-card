from aiogram.types import InlineKeyboardButton as Btn
from aiogram.types import InlineKeyboardMarkup

from bot.db.models import Booking, BookingStatus, Category, Product

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
            [Btn(text="\U0001f4e6 Каталог", callback_data="admin:catalog")],
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


# ── Catalog management ────────────────────────────────────────────


def admin_categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    buttons = [[Btn(text=f"{c.emoji} {c.name}", callback_data=f"admin:cat:{c.id}")] for c in categories]
    buttons.append([Btn(text="\u2795 Добавить категорию", callback_data="admin:cat:add")])
    buttons.append([Btn(text="\u2b05\ufe0f Админ-панель", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_category_kb(category: Category) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [Btn(text="\U0001f4e6 Товары", callback_data=f"admin:cat:products:{category.id}")],
            [Btn(text="\u270f\ufe0f Редактировать", callback_data=f"admin:cat:edit:{category.id}")],
            [Btn(text="\U0001f5d1 Удалить", callback_data=f"admin:cat:delete:{category.id}")],
            [Btn(text="\u2b05\ufe0f Каталог", callback_data="admin:catalog")],
        ]
    )


def admin_products_kb(products: list[Product], category_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [Btn(text=f"{p.name} — {p.price}\u20bd", callback_data=f"admin:prod:{p.id}")] for p in products
    ]
    buttons.append([Btn(text="\u2795 Добавить товар", callback_data=f"admin:prod:add:{category_id}")])
    buttons.append([Btn(text="\u2b05\ufe0f Категория", callback_data=f"admin:cat:{category_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_product_kb(product: Product) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [Btn(text="\u270f\ufe0f Редактировать", callback_data=f"admin:prod:edit:{product.id}")],
            [Btn(text="\U0001f5d1 Удалить", callback_data=f"admin:prod:delete:{product.id}")],
            [Btn(text="\u2b05\ufe0f Товары", callback_data=f"admin:cat:products:{product.category_id}")],
        ]
    )
