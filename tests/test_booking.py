from bot.services.booking import format_booking_notification, validate_phone


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
