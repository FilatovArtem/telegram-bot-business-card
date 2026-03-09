from aiogram.types import InlineKeyboardButton as Btn
from aiogram.types import InlineKeyboardMarkup

from bot.db.models import Category, Product


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    buttons = [
        [Btn(text=f"{cat.emoji} {cat.name}", callback_data=f"cat:{cat.id}")]
        for cat in categories
    ]
    buttons.append(
        [Btn(text="\u2b05\ufe0f \u041d\u0430\u0437\u0430\u0434", callback_data="main_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_card_kb(
    product: Product,
    idx: int,
    total: int,
    category_id: int,
) -> InlineKeyboardMarkup:
    nav_buttons: list[Btn] = []
    if idx > 0:
        nav_buttons.append(
            Btn(text="\u2b05\ufe0f", callback_data=f"prod:{category_id}:{idx - 1}")
        )
    nav_buttons.append(Btn(text=f"{idx + 1}/{total}", callback_data="noop"))
    if idx < total - 1:
        nav_buttons.append(
            Btn(text="\u27a1\ufe0f", callback_data=f"prod:{category_id}:{idx + 1}")
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_buttons,
            [Btn(
                text="\ud83d\udcdd \u0417\u0430\u043a\u0430\u0437\u0430\u0442\u044c",
                callback_data=f"order:{product.id}",
            )],
            [Btn(
                text="\u2b05\ufe0f \u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438",
                callback_data="catalog",
            )],
        ]
    )
