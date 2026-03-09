# Backlog

## In Progress

## Next
<!-- Финишная прямая: merge, CI, README, done. -->

- [ ] merge feat/product-features → main
- [ ] ci: GitHub Actions — lint + test + docker build, бейдж в README
- [ ] docs: обновить README — отразить новые фичи (статусы, управление каталогом, бизнес-конфиг)

## Later
<!-- Не блокируют портфолио -->

- [ ] test(core): расширить покрытие (repositories, FSM flow)
- [ ] feat(payments): Telegram Payments API
- [ ] feat(deploy): webhook mode (nginx + SSL)
- [ ] fix(broadcast): rate limiting на рассылку

## Done
- [x] refactor(config): бизнес-тексты из JSON, вход в booking через каталог — 2026-03-09
- [x] feat(booking): статусы заявок + управление из админки — 2026-03-09
- [x] feat(admin): управление каталогом через бот (CRUD категорий и товаров) — 2026-03-09
- [x] feat(db): Alembic миграции, замена create_all() — 2026-03-09
- [x] refactor(admin): router-level AdminFilter вместо _is_admin() в каждом handler — 2026-03-09
