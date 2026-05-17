# Backlog

## In Progress

## Next

## Later
<!-- Не блокируют портфолио -->

### Tech debt / quality
- [ ] test(handlers): router-factory pattern для размораживания 3 skipped integration tests (booking happy path, invalid phone, admin status transition)
- [ ] test(coverage): поднять `--cov-fail-under` 50 → 60 после router-factory fix
- [ ] refactor(callbacks): aiogram `CallbackData` factory вместо строкового parsing (cb_int helper заменить на typed payloads)
- [ ] refactor(fsm): переименовать `BookingForm.phone` → `BookingForm.entering_phone` (consistency с constitution FSM Contract)
- [ ] chore(repo): использовать `get_recent_bookings` в admin stats ИЛИ удалить (pre-existing dead code в repositories.py:82)

### Production hardening
- [ ] observability: structlog JSON + Sentry integration (когда появится реальная нагрузка от клиента)
- [ ] fsm-storage: RedisStorage для FSM (когда переезд на multi-replica)
- [ ] backup: cron job для SQLite/Postgres на сервере + off-site rsync (Hetzner Storage Box)
- [ ] healthcheck: Docker HEALTHCHECK через touch-file heartbeat (procps install заблокирован на хосте → нужен другой механизм)
- [ ] fix(broadcast): rate limiting per-user (сейчас только глобальный 50ms sleep между сообщениями)
- [ ] security: IP whitelist в SSH authorized_keys (`from="github.actions.cidrs"`) или restricted command для DEPLOY_SSH_KEY

### Features
- [ ] feat(payments): Telegram Stars для "чаевых мастеру" (wow-фича без сложности platform tokens)
- [ ] feat(payments): ЮKassa/T-Bank через provider_token (предоплата для физических услуг)
- [ ] feat(deploy): webhook mode + Caddy reverse_proxy + Let's Encrypt (отдельная ветка)
- [ ] feat(reminders): напоминание клиенту за 24 часа до записи (APScheduler / sqlite tasks)
- [ ] feat(catalog): inline calendar для выбора даты (aiogram3-calendar, RU-локаль)
- [ ] feat(analytics): UTM tracking в `/start utm=facebook` для атрибуции трафика
- [ ] test(e2e): расширить покрытие FSM happy path до edge cases (timeout, partial input)

## Done
- [x] refactor(config): бизнес-тексты из JSON, вход в booking через каталог — 2026-03-09
- [x] feat(booking): статусы заявок + управление из админки — 2026-03-09
- [x] feat(admin): управление каталогом через бот (CRUD категорий и товаров) — 2026-03-09
- [x] feat(db): Alembic миграции, замена create_all() — 2026-03-09
- [x] refactor(admin): router-level AdminFilter вместо _is_admin() в каждом handler — 2026-03-09
- [x] refactor(foundation): _utils.py helpers, Msg constants, BusinessConfigError, fail-soft seed — 2026-05-16
- [x] feat(startup): build_dispatcher + run coroutine, single asyncio.run() — 2026-05-16
- [x] feat(errors): global @dp.error() handler с уведомлениями админа — 2026-05-16
- [x] infra(docker): multi-stage Dockerfile, non-root, HEALTHCHECK, postgres profile — 2026-05-16
- [x] ci: GitHub Actions — ruff + mypy strict + pytest --cov + docker build + smoke test — 2026-05-16
- [x] test(coverage): 48 тестов, coverage 51.52% — 2026-05-16
- [x] docs: README rewrite + CHANGELOG v1.0.0 + CONTRIBUTING + GitHub templates — 2026-05-16
- [x] docs: docs/configuration.md + docs/deploy.md — 2026-05-16
- [x] chore: merge feat/mvp-release → main — 2026-05-16
- [x] ci(deploy): auto-deploy на NixOS home server через GitHub Actions (workflow_run trigger, appleboy/ssh-action) — 2026-05-17
- [x] fix(network): BOT_PROXY поддержка через AiohttpSession + network_mode: host (ISP блокирует Telegram) — 2026-05-17
- [x] fix(deps): aiohttp-socks для proxy support в aiogram — 2026-05-17
- [x] fix(docker): drop pgrep healthcheck (apt access blocked в sandboxed network) — 2026-05-17
- [x] fix(logging): preserve bot loggers после Alembic fileConfig() (force=True + disable_existing_loggers=False) — 2026-05-17
- [x] chore(repo): visibility PUBLIC → PRIVATE — 2026-05-17
