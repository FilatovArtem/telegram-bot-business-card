import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.db.engine import async_session, engine
from bot.db.models import Base
from bot.handlers import setup_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.services.catalog import seed_catalog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await seed_catalog(session)
    logger.info("Database initialized and seeded")


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.include_router(setup_routers())

    dp.startup.register(on_startup)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
