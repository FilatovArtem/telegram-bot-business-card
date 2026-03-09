from aiogram.types import InlineKeyboardButton as Btn
from aiogram.types import InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                Btn(
                    text="\ud83c\udf70 \u041a\u0430\u0442\u0430\u043b\u043e\u0433",
                    callback_data="catalog",
                ),
                Btn(
                    text="\ud83d\udcdd \u0417\u0430\u043f\u0438\u0441\u0430\u0442\u044c\u0441\u044f",
                    callback_data="booking",
                ),
            ],
            [
                Btn(
                    text="\u2139\ufe0f \u041e \u043d\u0430\u0441",
                    callback_data="about",
                ),
                Btn(
                    text="\ud83d\udcde \u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b",
                    callback_data="contacts",
                ),
            ],
        ]
    )


def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [Btn(
                text="\u2b05\ufe0f \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e",
                callback_data="main_menu",
            )],
        ]
    )
