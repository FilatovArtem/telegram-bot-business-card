from typing import ClassVar


class Msg:
    # Booking
    NAME_TOO_SHORT = "Имя слишком короткое. Введите ещё раз:"
    PHONE_INVALID = "❌ Неверный формат телефона.\nПример: +7 (XXX) XXX-XX-XX"
    DATE_TOO_SHORT = "Уточните дату, пожалуйста:"
    BOOKING_ACCEPTED = "✅ Заявка #{id} принята! Мы свяжемся с вами."
    BOOKING_CANCELLED = "❌ Заявка отменена."

    # Catalog
    CATALOG_EMPTY = "Каталог пока пуст. Загляните позже."
    NOT_FOUND_PRODUCT = "❌ Товар не найден."
    NOT_FOUND_CATEGORY = "❌ Категория не найдена."
    NOT_FOUND_BOOKING = "❌ Заявка не найдена."

    # Admin — catalog mutations
    CATEGORY_CREATED = "✅ Категория «{emoji} {name}» создана."
    CATEGORY_UPDATED = "✅ Категория обновлена: «{emoji} {name}»"
    CATEGORY_DELETED = "✅ Категория удалена."
    CATEGORY_HAS_PRODUCTS = "❌ Нельзя удалить — в категории есть товары."
    PRODUCT_CREATED = "✅ Товар «{name}» добавлен ({price} ₽)."
    PRODUCT_UPDATED = "✅ Товар обновлён: «{name}» ({price} ₽)"
    PRODUCT_DELETED = "✅ Товар удалён."
    NAME_TOO_SHORT_RETRY = "Название слишком короткое. Попробуйте ещё раз:"
    ENTER_NUMBER = "Введите число:"
    BROADCAST_CANCELLED = "Рассылка отменена."
    BROADCAST_RESULT = "Отправлено: {sent}. Не удалось: {failed}."

    # Generic
    GENERIC_ERROR = "❌ Произошла ошибка. Мы уже работаем над этим."
    CANCEL_AND_RETURN = "Отменено. Возврат в меню."
    ACTION_CANCELLED = "❌ Действие отменено."

    # Status labels
    STATUS_LABELS: ClassVar[dict[str, str]] = {
        "new": "🆕 Новая",
        "confirmed": "✅ Подтверждена",
        "completed": "✔️ Выполнена",
        "cancelled": "❌ Отменена",
    }
