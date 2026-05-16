# Configuration

## Бизнес-конфиг (data/business.json)

Все тексты и контакты бота вынесены в JSON — меняйте без правки кода.

Поля:
- `name` — название бизнеса (показывается в welcome)
- `welcome` — приветственное сообщение
- `about` — текст для кнопки "О нас"
- `contacts.phone, .email, .address, .hours` — для кнопки "Контакты"

После изменения JSON — перезапустите бот (`docker compose restart bot`).

Если JSON отсутствует или невалиден — бот не стартует с понятной ошибкой.

## Начальный каталог (data/seed.json)

Применяется ТОЛЬКО при первом запуске, когда БД пустая. Дальше каталог редактируется через `/admin` → 🛍️ Каталог.

Структура:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Торты",
      "emoji": "🎂",
      "products": [
        {"name": "Медовик", "description": "1.5 кг", "price": 2500, "image_url": null}
      ]
    }
  ]
}
```

Если seed.json отсутствует или невалиден — бот стартует, каталог пустой; админ заполнит через UI.

## Переменные окружения (.env)

| Переменная | Required | Описание |
|---|---|---|
| `BOT_TOKEN` | да | Токен от @BotFather, формат `<digits>:<alphanumeric>` |
| `ADMIN_IDS` | да | Telegram user_id админов через запятую |
| `ADMIN_CHAT_ID` | нет | Куда слать уведомления о заявках; если 0 — не шлёт |
| `DATABASE_URL` | нет | По умолчанию `sqlite+aiosqlite:///data/bot.db` |

## Получение токенов

### BOT_TOKEN
1. Telegram → найти **@BotFather**
2. `/newbot` → имя → username (заканчивается на `bot`)
3. BotFather пришлёт `Use this token to access the HTTP API: 123456:AAH...` — это и есть BOT_TOKEN

При утечке: BotFather → `/mybots` → бот → **API Token** → Revoke.

### ADMIN_IDS
Узнайте свой user_id у **@userinfobot** (Start → бот пришлёт ID).
Альтернатива: **@getmyid_bot**.

Формат в .env: `ADMIN_IDS=123456789` или `ADMIN_IDS=123456789,987654321` (через запятую).

### ADMIN_CHAT_ID

**Вариант A (личка):** используйте свой user_id (тот же что в `ADMIN_IDS`). Сначала напишите боту `/start`, иначе бот не сможет инициировать беседу.

**Вариант B (группа):**
1. Создайте группу, добавьте бот как админа
2. Добавьте **@RawDataBot** в группу
3. RawDataBot пришлёт JSON — найдите `"chat":{"id": -1001234567890, ...}`
4. Удалите RawDataBot

**Вариант C (через API):**
```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates" | jq '.result[-1].message.chat.id'
```

## Команды бота в Telegram

Установите через BotFather → `/setcommands`:

```
start - Главное меню
admin - Админ-панель (только для администраторов)
```

## База данных

**SQLite (default)** — файл `data/bot.db`. Подходит для production до ~100K users. Бэкап: `cp data/bot.db backups/bot-$(date +%F).db`.

**PostgreSQL** — для concurrent writes (несколько мастеров одновременно):
```bash
docker compose --profile postgres up -d
```
И в `.env`:
```
DATABASE_URL=postgresql+asyncpg://bot:bot@postgres:5432/bot
```
