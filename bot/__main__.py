import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from alembic import command
from alembic.config import Config

from bot.config import settings
from bot.db.engine import async_session
from bot.handlers import setup_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.services.business import load_business_config
from bot.services.catalog import seed_catalog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def on_startup() -> None:
    run_migrations()
    async with async_session() as session:
        await seed_catalog(session)
    logger.info("Database initialized and seeded")


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    bot["business"] = load_business_config()

    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.include_router(setup_routers())

    dp.startup.register(on_startup)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
