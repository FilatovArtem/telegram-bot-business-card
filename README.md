# SweetDream Bot - Telegram-бот для кондитерской

Telegram-бот для малого бизнеса: каталог товаров, онлайн-запись, уведомления администратору, рассылка.

## Проблема

Малый бизнес теряет клиентов, принимая заявки только по телефону. Бот работает 24/7, показывает каталог и принимает заявки автоматически.

## Решение

Telegram-бот с каталогом товаров, пошаговой формой записи (FSM), уведомлениями администратору и админ-панелью для управления заявками.

## Возможности

- **Каталог** - категории, карточки товаров с фото, навигация inline-кнопками
- **Запись** - пошаговая форма (FSM): услуга -> имя -> телефон -> дата -> подтверждение
- **Уведомления** - администратор получает заявку в реальном времени
- **Админ-панель** - статистика, просмотр заявок, рассылка по подписчикам
- **Валидация** - проверка формата телефона, защита от пустых полей

## Стек

Python 3.12 | aiogram 3 | SQLAlchemy 2 (async) | aiosqlite | Docker

> Production-вариант с PostgreSQL: раскомментируйте секцию в `docker-compose.yml` и измените `DATABASE_URL`.

## Быстрый старт

```bash
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
cp .env.example .env
# Заполните BOT_TOKEN и ADMIN_IDS в .env
docker-compose up --build
```

### Без Docker

```bash
pip install uv
uv pip install .
python -m bot
```

## Архитектура

```mermaid
graph TD
    U[User] -->|message| BOT[aiogram Bot]
    BOT --> MW[DB Middleware]
    MW --> R{Router}
    R --> START[/start - меню]
    R --> CAT[Каталог]
    R --> BOOK[Запись FSM]
    R --> ADM[Админ-панель]
    BOOK -->|уведомление| ADMIN[Admin Chat]
    CAT --> DB[(SQLite/PostgreSQL)]
    BOOK --> DB
```

## Структура проекта

```
bot/
├── __main__.py       # Точка входа
├── config.py         # Pydantic Settings
├── db/               # SQLAlchemy models + repositories
├── handlers/         # Обработчики команд и callback
├── keyboards/        # Inline-клавиатуры
├── middlewares/       # DB session injection
└── services/         # Бизнес-логика
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

Артем Филатов | Мехмат МГУ | [@Siki_sing](https://t.me/Siki_sing)
