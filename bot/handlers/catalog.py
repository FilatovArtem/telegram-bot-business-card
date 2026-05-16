from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Product
from bot.db.repositories import get_categories, get_products_by_category
from bot.handlers._utils import cb_data, cb_int, cb_message
from bot.keyboards.catalog import categories_kb, product_card_kb
from bot.keyboards.main_menu import back_to_menu_kb
from bot.services.messages import Msg

router = Router()


@router.callback_query(F.data == "catalog")
async def cb_catalog(callback: CallbackQuery, session: AsyncSession) -> None:
    categories = await get_categories(session)
    msg = cb_message(callback)
    await msg.delete()
    if not categories:
        await msg.answer(Msg.CATALOG_EMPTY, reply_markup=back_to_menu_kb())
        await callback.answer()
        return
    await msg.answer(
        "\U0001f4cb <b>Выберите категорию:</b>",
        reply_markup=categories_kb(categories),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = cb_int(cb_data(callback), 1)
    if category_id is None:
        await callback.answer()
        return
    products = await get_products_by_category(session, category_id)
    if not products:
        await callback.answer("В этой категории пока нет товаров")
        return
    await _show_product(callback, products, 0, category_id)


@router.callback_query(F.data.startswith("prod:"))
async def cb_product_nav(callback: CallbackQuery, session: AsyncSession) -> None:
    data = cb_data(callback)
    category_id = cb_int(data, 1)
    idx = cb_int(data, 2)
    if category_id is None or idx is None:
        await callback.answer()
        return
    products = await get_products_by_category(session, category_id)
    if not products or idx >= len(products):
        await callback.answer(Msg.NOT_FOUND_PRODUCT)
        return
    await _show_product(callback, products, idx, category_id)


async def _show_product(
    callback: CallbackQuery,
    products: list[Product],
    idx: int,
    category_id: int,
) -> None:
    product = products[idx]
    text = f"<b>{product.name}</b>\n\n{product.description}\n\n\U0001f4b0 Цена: {product.price} руб."
    kb = product_card_kb(product, idx, len(products), category_id)

    msg = cb_message(callback)
    await msg.delete()

    if product.image_url:
        await msg.answer_photo(
            photo=product.image_url,
            caption=text,
            reply_markup=kb,
        )
    else:
        await msg.answer(text, reply_markup=kb)
    await callback.answer()
