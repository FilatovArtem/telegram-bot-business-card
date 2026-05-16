# Changelog

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), проект следует [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-16

### Added
- MVP-релиз: каталог, FSM booking, админ-панель, CRUD каталога, статусы заявок (new → confirmed → completed / cancelled)
- Бизнес-конфиг через `data/business.json` (адаптация без правки кода)
- Глобальный `@dp.error()` handler с уведомлениями админа
- Multi-stage Dockerfile (uv 0.5.11, non-root user, HEALTHCHECK)
- docker-compose с healthcheck, log rotation, optional postgres profile
- CI (GitHub Actions): ruff + mypy strict + pytest --cov + docker build
- Pre-commit hooks: ruff + ruff-format + mypy
- Inline cancel-кнопка в каждом шаге booking FSM
- Глобальный `/cancel` handler — работает на любых FSM
- `Msg` класс с константами user-facing текста (единый тон)
- `cb_message/cb_data/cb_int` helpers — устранили ~30 `# type: ignore` в handlers
- Repository pattern строго: handlers без ORM-запросов
- ~48 тестов: services, repositories, filters, callbacks, error handler

### Changed
- `bot/__main__.py` — single `asyncio.run()` (single async startup pipeline через `bot/startup.py`)
- Settings field_validators: fail-fast на missing/invalid `BOT_TOKEN`, `ADMIN_IDS`
- `seed_catalog` — fail-soft на missing/malformed `data/seed.json`
- `load_business_config` — fail-fast с `BusinessConfigError` на missing/malformed/invalid-schema
- Broadcast в admin — `asyncio.sleep(0.05)` между сообщениями (safe от Telegram limits)

### Security
- Non-root user в Docker (uid 1000)
- `.env` validation на startup
- Handlers не логируют сырые `message.text` (защита PII)

### Fixed
- `get_bookings_by_status` — secondary order by `id DESC` (защита от равных timestamp'ов при быстрых вставках)
