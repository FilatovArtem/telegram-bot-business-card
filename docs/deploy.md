# Deploy

## Локально (Docker)

```bash
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
cp .env.example .env  # заполните токены
docker compose up --build -d
docker compose logs -f bot
```

Healthcheck: `docker compose ps` → должен показать `healthy` через 30-60 сек.

## Локально (без Docker)

```bash
pip install uv
uv sync
uv run python -m bot
```

## VPS (рекомендация: Hetzner CX22 ~€3.79/мес)

```bash
# На сервере (Ubuntu/Debian)
apt update && apt install -y docker.io docker-compose-plugin git
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
cp .env.example .env
nano .env  # заполните токены
docker compose up -d --build
```

Restart policy `unless-stopped` уже включён — бот перезапустится после reboot сервера.

## Логи

```bash
docker compose logs -f bot       # tail логов
docker compose logs --tail 200 bot
```

Log rotation: json-file driver, 10 MB × 3 файла (configured в `docker-compose.yml`).

## Бэкап SQLite

```bash
# Простая копия (без транзакций — для маленькой нагрузки OK)
cp data/bot.db backups/bot-$(date +%F).db

# Cron job (каждую ночь в 03:00, держать 30 дней)
crontab -e
# 0 3 * * * cd /path/to/bot && cp data/bot.db backups/bot-$(date +\%F).db && find backups/ -name 'bot-*.db' -mtime +30 -delete
```

Off-site: rsync на S3-compatible (Hetzner Storage Box, Backblaze B2).

## PostgreSQL (опциональный профиль)

Если ожидаете concurrent writes:

```bash
docker compose --profile postgres up -d
```

В `.env`:
```
DATABASE_URL=postgresql+asyncpg://bot:bot@postgres:5432/bot
POSTGRES_USER=bot
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=bot
```

Бэкап:
```bash
docker compose exec postgres pg_dump -U bot bot | gzip > backups/db-$(date +%F).sql.gz
```

## Webhook режим

В MVP бот работает в long-polling режиме. Webhook — отдельная задача (см. `specs/backlog.md` Later).

## Update бота

```bash
git pull
docker compose up -d --build
```

Alembic миграции применяются автоматически при старте.
