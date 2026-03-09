from aiogram import Router

from bot.handlers.admin import router as admin_router
from bot.handlers.booking import router as booking_router
from bot.handlers.catalog import router as catalog_router
from bot.handlers.start import router as start_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(admin_router)
    root.include_router(booking_router)
    root.include_router(catalog_router)
    root.include_router(start_router)
    return root
