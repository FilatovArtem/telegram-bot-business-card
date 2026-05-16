# Backlog

## In Progress

## Next

## Later
<!-- Не блокируют портфолио -->

- [ ] feat(payments): Telegram Payments API
- [ ] feat(deploy): webhook mode (nginx + SSL)
- [ ] fix(broadcast): rate limiting на рассылку
- [ ] test(core): расширить покрытие (FSM flow e2e)

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
