from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import get_categories, get_products_by_category
from bot.keyboards.catalog import categories_kb, product_card_kb

router = Router()


@router.callback_query(F.data == "catalog")
async def cb_catalog(callback: CallbackQuery, session: AsyncSession) -> None:
    categories = await get_categories(session)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "📋 <b>Выберите категорию:</b>",
        reply_markup=categories_kb(categories),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[1])  # type: ignore[union-attr]
    products = await get_products_by_category(session, category_id)
    if not products:
        await callback.answer("В этой категории пока нет товаров")
        return
    await _show_product(callback, products, 0, category_id)


@router.callback_query(F.data.startswith("prod:"))
async def cb_product_nav(callback: CallbackQuery, session: AsyncSession) -> None:
    parts = callback.data.split(":")  # type: ignore[union-attr]
    category_id = int(parts[1])
    idx = int(parts[2])
    products = await get_products_by_category(session, category_id)
    if not products or idx >= len(products):
        await callback.answer("Товар не найден")
        return
    await _show_product(callback, products, idx, category_id)


async def _show_product(
    callback: CallbackQuery,
    products: list,  # type: ignore[type-arg]
    idx: int,
    category_id: int,
) -> None:
    product = products[idx]
    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f"💰 Цена: {product.price} руб."
    )
    kb = product_card_kb(product, idx, len(products), category_id)

    if product.image_url:
        # If product has an image, send photo instead
        await callback.message.delete()  # type: ignore[union-attr]
        await callback.message.answer_photo(  # type: ignore[union-attr]
            photo=product.image_url,
            caption=text,
            reply_markup=kb,
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(  # type: ignore[union-attr]
            text, reply_markup=kb, parse_mode="HTML"
        )
    await callback.answer()
