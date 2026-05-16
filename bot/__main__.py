import asyncio
import logging

from alembic import command
from alembic.config import Config

from bot.config import settings  # noqa: F401 — triggers validators + SystemExit if invalid
from bot.startup import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        logger.exception("Migration failed — aborting startup")
        raise SystemExit(1) from e
    asyncio.run(run())
