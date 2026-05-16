# Contributing

## Локальная настройка

```bash
git clone https://github.com/FilatovArtem/telegram-bot-business-card.git
cd telegram-bot-business-card
uv sync --extra dev
cp .env.example .env
# Заполните BOT_TOKEN и ADMIN_IDS — см. docs/configuration.md
uv run python -m bot
```

## Workflow

- Ветка от `main`: `type/short-description` (например, `feat/inline-calendar`)
- Conventional Commits: `type(scope): описание`
- Типы: feat, fix, refactor, docs, test, chore, ci, perf

## Перед коммитом

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy bot
uv run pytest -v
```

Или установите pre-commit (запускает всё автоматически):
```bash
uv run pre-commit install
```

## Code style

- Python 3.12, type hints обязательны (mypy strict)
- ruff: line-length 110, селекторы `E, F, I, N, UP, ANN, B, A, SIM, PT, RUF, S`
- Repositories pattern: вся работа с БД через `bot/db/repositories.py` (не в handlers)
- Бизнес-логика в `bot/services/`, не в handlers
- User-facing строки — через `Msg` в `bot/services/messages.py`

## Архитектурные правила

См. [.specify/memory/constitution.md](.specify/memory/constitution.md):
- Simplicity First — нет лишних абстракций
- Surgical Changes — трогай только необходимое
- Test What Breaks Production — покрывай валидацию, FSM, репозитории
