import json
from pathlib import Path

import pytest

from bot.services.business import BusinessConfig, BusinessConfigError, load_business_config

VALID_BUSINESS_JSON = {
    "name": "TestBiz",
    "welcome": "Добро пожаловать!",
    "about": "О нас",
    "contacts": {
        "phone": "+7 (495) 123-45-67",
        "email": "hello@test.ru",
        "address": "Москва",
        "hours": "9:00-21:00",
    },
}


def test_load_valid_json_returns_business_config(tmp_path: Path) -> None:
    config_file = tmp_path / "business.json"
    config_file.write_text(json.dumps(VALID_BUSINESS_JSON), encoding="utf-8")

    result = load_business_config(str(config_file))

    assert isinstance(result, BusinessConfig)
    assert result.name == "TestBiz"
    assert result.contacts.phone == "+7 (495) 123-45-67"
    assert result.contacts.email == "hello@test.ru"


def test_load_missing_file_raises_business_config_error() -> None:
    with pytest.raises(BusinessConfigError):
        load_business_config("/nonexistent/path/business.json")


def test_load_malformed_json_raises_business_config_error_with_invalid_json(tmp_path: Path) -> None:
    bad_file = tmp_path / "business.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(BusinessConfigError, match="Invalid JSON"):
        load_business_config(str(bad_file))


def test_load_invalid_schema_missing_contacts_raises_business_config_error(tmp_path: Path) -> None:
    incomplete = {"name": "TestBiz", "welcome": "hi", "about": "about"}
    config_file = tmp_path / "business.json"
    config_file.write_text(json.dumps(incomplete), encoding="utf-8")

    with pytest.raises(BusinessConfigError, match="schema invalid"):
        load_business_config(str(config_file))
