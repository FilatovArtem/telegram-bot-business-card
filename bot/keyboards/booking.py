from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Отменить", callback_data="booking:cancel")]]
    )


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="booking:confirm:yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="booking:confirm:no"),
            ],
        ]
    )
