import re

from bot.db.models import BookingStatus

PHONE_PATTERN = re.compile(r"^(\+7|8)\s?\(?\d{3}\)?\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}$")

STATUS_USER_LABELS: dict[str, str] = {
    BookingStatus.NEW: "Новая",
    BookingStatus.CONFIRMED: "Подтверждена",
    BookingStatus.COMPLETED: "Завершена",
    BookingStatus.CANCELLED: "Отменена",
}


def format_status_label(status: str) -> str:
    return STATUS_USER_LABELS.get(status, status)


def format_status_change_notification(booking_id: int, service: str, new_status: str) -> str:
    label = format_status_label(new_status)
    return (
        f"\U0001f514 <b>Статус заявки #{booking_id} изменён</b>\n\n"
        f"\U0001f382 {service}\n"
        f"\U0001f4cb Статус: {label}"
    )


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
