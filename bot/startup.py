import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from bot.config import settings
from bot.db.engine import async_session, engine
from bot.handlers import setup_routers
from bot.handlers.errors import register_error_handler
from bot.middlewares.db import DbSessionMiddleware
from bot.services.business import BusinessConfigError, load_business_config
from bot.services.catalog import seed_catalog

logger = logging.getLogger(__name__)


async def _seed_db() -> None:
    async with async_session() as session:
        await seed_catalog(session)


def build_dispatcher(bot: Bot) -> Dispatcher:
    try:
        business = load_business_config()
    except BusinessConfigError as e:
        logger.error("Failed to load business config: %s", e)
        raise SystemExit(f"Required config missing or invalid: {e}") from e

    dp = Dispatcher()
    dp["business"] = business
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=async_session))
    dp.include_router(setup_routers())
    register_error_handler(dp, bot)
    return dp


async def run() -> None:
    """Единая async-coroutine: seed + polling. Migrations — sync до event loop."""
    try:
        await _seed_db()
    except Exception:
        logger.exception("Seed failed — continuing without demo data")

    session = AiohttpSession(proxy=settings.bot_proxy) if settings.bot_proxy else None
    if session is not None:
        logger.info("Telegram API via proxy: %s", settings.bot_proxy)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
        session=session,
    )
    dp = build_dispatcher(bot)

    logger.info("Bot starting: polling mode, %d admin(s)", len(settings.admin_ids))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Shutting down: dispose engine")
        await bot.session.close()
        await engine.dispose()
