# Auto-deploy на NixOS home server

Этот гайд настраивает автодеплой бота из GitHub в существующий контейнер на домашнем сервере (NixOS 25.05 + Docker).

## Архитектура

```
git push origin main
       │
       ▼
GitHub Actions: CI (ruff + mypy + pytest + docker build)
       │ (если green)
       ▼
GitHub Actions: Deploy (workflow_run trigger)
       │ SSH
       ▼
Сервер: git fetch + reset --hard origin/main + docker compose up -d --build
       │
       ▼
Бот перезапускается с новой версией (HEALTHCHECK + restart: unless-stopped)
```

## Что уже готово в репо

- `.github/workflows/ci.yml` — линт + тесты + docker build smoke test
- `.github/workflows/deploy.yml` — auto-deploy после успешного CI
- `Dockerfile` (multi-stage, non-root) + `docker-compose.yml` (healthcheck + restart unless-stopped)

## Одноразовая подготовка

### 1. Сгенерируйте deploy SSH key (локально)

```bash
ssh-keygen -t ed25519 -N "" -C "github-actions-deploy-tgbot" -f ~/.ssh/tgbot_deploy
```

Получите два файла:
- `~/.ssh/tgbot_deploy` — приватный (для GitHub secret)
- `~/.ssh/tgbot_deploy.pub` — публичный (для сервера)

### 2. Добавьте публичный ключ на сервер

```bash
cat ~/.ssh/tgbot_deploy.pub | ssh nixos-home-server 'cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

Можно ограничить ключ только нужной командой (опционально, для безопасности):

```bash
# Вместо обычного "ssh-ed25519 AAAA... comment" — добавить with restrictions:
# command="cd /home/admin/telegram-bot-business-card && bash -lc 'git fetch --prune origin main && git reset --hard origin/main && docker compose up -d --build --remove-orphans'",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty ssh-ed25519 AAAA... comment
```

⚠️ Restriction ломает `workflow_dispatch` (manual trigger) если команда меняется. Опционально.

### 3. Получите fingerprint сервера (для secret)

```bash
ssh-keyscan -t ed25519 95.165.71.0
```

(Сохраните вывод — на случай если потребуется проверять host key вручную.)

### 4. Добавьте GitHub secrets

В GitHub: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Value |
|---|---|
| `DEPLOY_HOST` | `95.165.71.0` (публичный IP сервера) |
| `DEPLOY_USER` | `admin` |
| `DEPLOY_SSH_KEY` | Содержимое файла `~/.ssh/tgbot_deploy` (полностью, включая `-----BEGIN OPENSSH PRIVATE KEY-----` и `-----END OPENSSH PRIVATE KEY-----`) |

### 5. Заполните `.env` на сервере

```bash
ssh nixos-home-server
cd /home/admin/telegram-bot-business-card
nano .env
```

Заполните значения (см. `docs/configuration.md` где их взять):

```
BOT_TOKEN=<токен от @BotFather>
ADMIN_IDS=<ваш Telegram user_id>
ADMIN_CHAT_ID=<куда слать уведомления о заявках>
DATABASE_URL=sqlite+aiosqlite:///data/bot.db
```

Проверьте права (`.env` должен быть 600):

```bash
chmod 600 .env
stat -c "%a %n" .env  # expect: 600 .env
```

### 6. Первый деплой (manual)

После того как `.env` заполнен, можно запустить деплой вручную:

**Через GitHub UI:** Actions → Deploy → Run workflow → выбрать `main`.

**Через SSH (sanity check):**

```bash
ssh nixos-home-server
cd /home/admin/telegram-bot-business-card
git fetch --prune origin main
git reset --hard origin/main
docker compose up -d --build --remove-orphans
docker compose ps          # должно показать STATUS: Up (healthy)
docker compose logs -f bot # tail логов; Ctrl+C для выхода
```

Проверка: в Telegram открыть бота → `/start` → должно прийти главное меню из `data/business.json`.

## Как работает auto-deploy после настройки

1. Локально: `git push origin main`
2. GitHub Actions автоматически:
   - Прогон **CI** (ruff + mypy + pytest + docker build smoke)
   - Если зелёный — триггерится **Deploy** workflow (через `workflow_run`)
   - Deploy открывает SSH к серверу и выполняет `git pull + docker compose up -d --build`
   - Health check: контейнер должен стать `healthy` через 30-60s, иначе Docker сам перезапустит
3. В Telegram бот доступен с новой версией

## Manual ручной деплой / rollback

**Manual trigger:** Actions → Deploy → **Run workflow** (можно даже когда нет push).

**Rollback на предыдущий коммит:**

```bash
ssh nixos-home-server
cd /home/admin/telegram-bot-business-card
git reset --hard <предыдущий-sha>
docker compose up -d --build
```

После rollback история git сервера и origin/main расходятся. Следующий push в main снова сделает hard reset.

## Логи и диагностика

```bash
ssh nixos-home-server
cd /home/admin/telegram-bot-business-card

docker compose ps                # статус контейнера
docker compose logs -f bot       # tail логов
docker compose logs --since 1h bot
docker compose exec bot ls /app/data  # данные SQLite в volume

# История деплоев (если включить логирование в deploy скрипте — сейчас не пишется в файл, только GitHub Actions UI)
```

GitHub Actions deploy логи: **Actions → Deploy → выбрать run**.

## Что не входит в текущий setup (опционально, если потребуется)

- **Webhook режим** — сейчас polling, не нужен open port. Если переключим на webhook, потребуется vhost в Caddy (`tgbot.95.165.71.0.nip.io` → `127.0.0.1:8080`). Прецедент в `~/.claude/memory/reference_nixos-home-server.md`.
- **Backup SQLite** — пример cron в `docs/deploy.md` §"Бэкап SQLite".
- **Sentry / structured logging** — в backlog Later.
- **Multi-environment** (staging) — пока single env (prod = home server).

## Безопасность

- Deploy SSH key хранится только в GitHub secrets (encrypted at rest, доступ только workflow runner)
- Приватный токен бота — в `.env` на сервере (chmod 600), никогда не в git
- HTTPS GitHub clone (no PAT needed для public repo)
- Контейнер от non-root user (uid 1000 внутри)
- При утечке `BOT_TOKEN` — @BotFather → `/mybots` → бот → **API Token** → **Revoke**

## Troubleshooting

**Deploy упал с `Permission denied (publickey)`:** SSH key не добавлен в `~/.ssh/authorized_keys` на сервере, либо неверный формат в `DEPLOY_SSH_KEY` secret (должен быть с переводами строк, OpenSSH формат).

**`Configuration error: BOT_TOKEN invalid`:** `.env` пустой или содержит fake-token. Заполните настоящий от @BotFather.

**Healthcheck unhealthy после deploy:** `docker compose logs bot` покажет причину. Чаще всего — невалидный `.env` или сломанная миграция.

**`Conflict: terminated by other getUpdates request`:** Запущен второй экземпляр бота (например, локально на ноутбуке + на сервере). Остановите лишнюю копию.

**Push отвергнут потому что upstream диверг (после rollback):** Это ожидаемо. Следующий push в `main` (force или нет — деплой делает hard reset, не использует merge) применит новую версию.
