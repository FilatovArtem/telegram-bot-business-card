import json
from pathlib import Path

from pydantic import BaseModel


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
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return BusinessConfig.model_validate(data)
