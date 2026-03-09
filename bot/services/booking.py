import re

PHONE_PATTERN = re.compile(r"^(\+7|8)\s?\(?\d{3}\)?\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}$")


def validate_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.match(phone.strip()))


def format_booking_notification(
    client_name: str,
    phone: str,
    service: str,
    desired_date: str,
    username: str | None = None,
) -> str:
    tg_link = f"@{username}" if username else "нет username"
    return (
        f"📋 <b>Новая заявка</b>\n\n"
        f"👤 Имя: {client_name}\n"
        f"📱 Телефон: {phone}\n"
        f"🔗 Telegram: {tg_link}\n"
        f"🎂 Услуга: {service}\n"
        f"📅 Дата: {desired_date}"
    )
