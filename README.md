# SweetDream Bot — Telegram-бот для кондитерской

[![CI](https://github.com/FilatovArtem/telegram-bot-business-card/actions/workflows/ci.yml/badge.svg)](https://github.com/FilatovArtem/telegram-bot-business-card/actions)

Telegram-бот для малого бизнеса: каталог товаров, онлайн-запись, управление заявками и каталогом через админ-панель.

## Проблема

Малый бизнес теряет клиентов, принимая заявки только по телефону. Бот работает 24/7, показывает каталог и принимает заявки автоматически.

## Возможности

- **Каталог** — категории, карточки товаров с навигацией inline-кнопками
- **Запись** — пошаговая форма (FSM): выбор товара → имя → телефон → дата → подтверждение
- **Статусы заявок** — new → confirmed → completed / cancelled, с уведомлением клиента
- **Админ-панель** — статистика, управление заявками по статусам, CRUD каталога, рассылка
- **Бизнес-конфиг** — название, тексты, контакты вынесены в `data/business.json`
- **Валидация** — проверка формата телефона, защита от пустых полей

## Стек

Python 3.12 · aiogram 3 · SQLAlchemy 2 (async) · Alembic · aiosqlite · pydantic-settings · Docker

## Быстрый старт

```bash
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
cp .env.example .env
# Заполните BOT_TOKEN и ADMIN_IDS в .env
docker compose up --build
```

### Без Docker

```bash
pip install uv
uv sync
uv run python -m bot
```

## Архитектура

```mermaid
graph TD
    U[User] -->|message| BOT[aiogram Bot]
    BOT --> MW[DB Middleware]
    MW --> R{Router}
    R --> START[/start — меню]
    R --> CAT[Каталог]
    R --> BOOK[Запись FSM]
    R --> ADM[Админ-панель]
    R --> ACAT[Управление каталогом]
    BOOK -->|уведомление| ADMIN[Admin Chat]
    ADM -->|смена статуса| U
    CAT --> DB[(SQLite / PostgreSQL)]
    BOOK --> DB
    ADM --> DB
    ACAT --> DB
```

## Структура проекта

```
bot/
├── __main__.py       # Точка входа, загрузка конфига
├── config.py         # Pydantic Settings
├── filters.py        # AdminFilter (shared)
├── db/               # SQLAlchemy models + repositories
├── handlers/         # start, catalog, booking, admin, admin_catalog
├── keyboards/        # Inline-клавиатуры
├── middlewares/       # DB session injection
└── services/         # Бизнес-логика, BusinessConfig
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/admin` | Админ-панель (только для ADMIN_IDS) |

## Переменные окружения

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC...` |
| `ADMIN_IDS` | ID администраторов (через запятую) | `123456789,987654321` |
| `ADMIN_CHAT_ID` | Чат для уведомлений о заявках | `123456789` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///data/bot.db` |

## Автор

Артем Филатов · Мехмат МГУ · [@Siki_sing](https://t.me/Siki_sing)
