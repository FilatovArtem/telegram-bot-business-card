import json
from pathlib import Path

from pydantic import BaseModel, ValidationError


class BusinessConfigError(RuntimeError):
    """Raised when business config can't be loaded or is invalid."""


class ContactsConfig(BaseModel):
    phone: str
    email: str
    address: str
    hours: str


class BusinessConfig(BaseModel):
    name: str
    welcome: str
    about: str
    contacts: ContactsConfig

    def welcome_html(self) -> str:
        return f"\U0001f370 <b>Добро пожаловать в {self.name}!</b>\n\n{self.welcome}"

    def about_html(self) -> str:
        return f"\U0001f3e0 <b>О нас</b>\n\n{self.about}"

    def contacts_html(self) -> str:
        c = self.contacts
        return (
            "\U0001f4de <b>Контакты</b>\n\n"
            f"\U0001f4f1 Телефон: {c.phone}\n"
            f"\U0001f4e7 Email: {c.email}\n"
            f"\U0001f4cd {c.address}\n"
            f"\U0001f550 Приём заказов: {c.hours}"
        )


def load_business_config(path: str = "data/business.json") -> BusinessConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise BusinessConfigError(f"Business config not found: {path}")
    try:
        raw = config_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise BusinessConfigError(f"Invalid JSON in {path}: {e}") from e
    try:
        return BusinessConfig.model_validate(data)
    except ValidationError as e:
        raise BusinessConfigError(f"Business config schema invalid: {e}") from e
