from aiogram.types import InlineKeyboardButton as Btn
from aiogram.types import InlineKeyboardMarkup


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [Btn(
                text="\ud83d\udcca \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430",
                callback_data="admin:stats",
            )],
            [Btn(
                text="\ud83d\udccb \u0417\u0430\u044f\u0432\u043a\u0438",
                callback_data="admin:bookings",
            )],
            [Btn(
                text="\ud83d\udce2 \u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0430",
                callback_data="admin:broadcast",
            )],
            [Btn(
                text="\u2b05\ufe0f \u041c\u0435\u043d\u044e",
                callback_data="main_menu",
            )],
        ]
    )
