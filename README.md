# SweetDream Bot

> Telegram-бот для малого бизнеса: каталог услуг, онлайн-запись, админ-панель. Настройки бизнеса вынесены в `data/business.json`.

[![CI](https://github.com/FilatovArtem/telegram-bot-business-card/actions/workflows/ci.yml/badge.svg)](https://github.com/FilatovArtem/telegram-bot-business-card/actions)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![aiogram 3](https://img.shields.io/badge/aiogram-3.13+-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

SweetDream - вымышленная кондитерская для демо. Клиент выбирает товар в каталоге и оставляет заявку. Администратор подтверждает её в Telegram, клиент получает уведомление.

## Возможности

- **Каталог** — категории, карточки товаров с навигацией inline-кнопками
- **Запись (FSM)** — пошаговая форма: товар → имя → телефон → дата → подтверждение
- **Статусы заявок** — new → confirmed → completed / cancelled, с уведомлением клиента
- **Админ-панель** — статистика, управление заявками, CRUD каталога, рассылка
- **Бизнес-конфиг** — название, тексты, контакты вынесены в `data/business.json`
- **Валидация** — проверка формата телефона, защита от пустых полей
- **Глобальный error handler** — бот не падает; админ получает уведомление
- **Production-ready Docker** — multi-stage, non-root, HEALTHCHECK

## Стек

Python 3.12 · aiogram 3 · SQLAlchemy 2 (async) · Alembic · aiosqlite (default) / asyncpg (optional) · pydantic-settings · Docker

## Быстрый старт

```bash
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
cp .env.example .env
# Заполните BOT_TOKEN, ADMIN_IDS, ADMIN_CHAT_ID в .env
# Где взять токены: docs/configuration.md
docker compose up --build
```

### Без Docker

```bash
pip install uv
uv sync
uv run python -m bot
```

Подробная настройка: [docs/configuration.md](docs/configuration.md)
Деплой на сервер: [docs/deploy.md](docs/deploy.md)

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
    BOOK -->|уведомление| ADMIN[Admin Chat]
    ADM -->|смена статуса| U
    CAT --> DB[(SQLite / PostgreSQL)]
    BOOK --> DB
    ADM --> DB
```

Полное описание архитектуры: [docs/architecture.md](docs/architecture.md)

## Структура проекта

```
bot/
├── __main__.py       # Тонкий entrypoint (logging + migrations + run)
├── startup.py        # build_dispatcher + run coroutine
├── config.py         # Pydantic Settings + validators
├── filters.py        # AdminFilter (shared)
├── db/               # SQLAlchemy models + repositories
├── handlers/         # start, catalog, booking, admin, admin_catalog, errors
├── keyboards/        # Inline-клавиатуры (cancel, confirm, navigation)
├── middlewares/      # DB session injection
└── services/         # Бизнес-логика, BusinessConfig, Msg константы
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню (сбрасывает FSM state) |
| `/cancel` | Отмена текущего действия |
| `/admin` | Админ-панель (только для ADMIN_IDS) |

## Переменные окружения

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC...` |
| `ADMIN_IDS` | Telegram user ID (через запятую) | `123456789,987654321` |
| `ADMIN_CHAT_ID` | Чат для уведомлений | `123456789` |
| `DATABASE_URL` | URL базы | `sqlite+aiosqlite:///data/bot.db` |

Подробно: [docs/configuration.md](docs/configuration.md)

## Адаптация под свой бизнес

1. **Тексты, название, контакты** — `data/business.json`. Без правки кода.
2. **Начальный каталог** — `data/seed.json` (применяется при первом запуске, если БД пустая).
3. **Управление каталогом в runtime** — через `/admin` → 🛍️ Каталог.

## Деплой

- VPS (Hetzner / Timeweb / любой Docker host): [docs/deploy.md](docs/deploy.md)
- Ручной деплой на NixOS-сервер через GitHub Actions: [docs/deploy-nixos.md](docs/deploy-nixos.md)

## Разработка

```bash
uv sync --extra dev
uv run ruff check . && uv run ruff format --check .
uv run mypy bot
uv run pytest -v
```

Pre-commit hooks: `uv run pre-commit install`

См. [CONTRIBUTING.md](CONTRIBUTING.md).

## Автор

Артём Филатов · [@sikisingg](https://t.me/sikisingg)

## Лицензия

[MIT](LICENSE)
