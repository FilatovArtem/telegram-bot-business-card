from bot.services.booking import (
    format_booking_notification,
    format_status_change_notification,
    format_status_label,
    validate_phone,
)


class TestValidatePhone:
    def test_valid_plus7(self) -> None:
        assert validate_phone("+79991234567")

    def test_valid_8(self) -> None:
        assert validate_phone("89991234567")

    def test_valid_formatted(self) -> None:
        assert validate_phone("+7 (999) 123-45-67")

    def test_invalid_short(self) -> None:
        assert not validate_phone("123")

    def test_invalid_letters(self) -> None:
        assert not validate_phone("abc")

    def test_empty(self) -> None:
        assert not validate_phone("")


class TestFormatNotification:
    def test_with_username(self) -> None:
        text = format_booking_notification(
            client_name="Иван",
            phone="+79991234567",
            service="Торт на заказ",
            desired_date="15 марта",
            username="ivan_test",
        )
        assert "Иван" in text
        assert "+79991234567" in text
        assert "@ivan_test" in text
        assert "Торт на заказ" in text

    def test_without_username(self) -> None:
        text = format_booking_notification(
            client_name="Иван",
            phone="+79991234567",
            service="Торт",
            desired_date="15 марта",
        )
        assert "нет username" in text


class TestFormatStatusLabel:
    def test_known_status_new(self) -> None:
        label = format_status_label("new")
        assert "Новая" in label

    def test_known_status_confirmed(self) -> None:
        label = format_status_label("confirmed")
        assert "Подтвержден" in label

    def test_unknown_status_falls_back_to_raw(self) -> None:
        label = format_status_label("mystery_status")
        assert label == "mystery_status"


class TestFormatStatusChangeNotification:
    def test_contains_booking_id_service_and_label(self) -> None:
        text = format_status_change_notification(
            booking_id=42,
            service="Торт на заказ",
            new_status="confirmed",
        )
        assert "42" in text
        assert "Торт на заказ" in text
        # Should contain human-readable label, not raw "confirmed"
        assert "Подтвержден" in text

    def test_contains_booking_id_for_cancelled(self) -> None:
        text = format_status_change_notification(
            booking_id=7,
            service="Капкейки",
            new_status="cancelled",
        )
        assert "7" in text
        assert "Отменена" in text
