from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import (
    create_category,
    create_product,
    delete_category,
    delete_product,
    get_categories,
    get_category,
    get_product,
    get_products_by_category,
    update_category,
    update_product,
)
from bot.filters import AdminFilter
from bot.keyboards.admin import (
    admin_categories_kb,
    admin_category_kb,
    admin_product_kb,
    admin_products_kb,
)

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


class CategoryForm(StatesGroup):
    name = State()
    emoji = State()


class CategoryEditForm(StatesGroup):
    name = State()
    emoji = State()


class ProductForm(StatesGroup):
    name = State()
    description = State()
    price = State()


class ProductEditForm(StatesGroup):
    name = State()
    description = State()
    price = State()


# ── Category list ─────────────────────────────────────────────────


@router.callback_query(F.data == "admin:catalog")
async def cb_admin_catalog(callback: CallbackQuery, session: AsyncSession) -> None:
    categories = await get_categories(session)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\U0001f4e6 <b>Управление каталогом</b>",
        reply_markup=admin_categories_kb(categories),
    )
    await callback.answer()


# ── Category card ─────────────────────────────────────────────────


@router.callback_query(F.data.regexp(r"^admin:cat:\d+$"))
async def cb_category_card(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    category = await get_category(session, category_id)
    if category is None:
        await callback.answer("Категория не найдена")
        return
    products = await get_products_by_category(session, category_id)
    text = f"{category.emoji} <b>{category.name}</b>\n\nТоваров: {len(products)}"
    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=admin_category_kb(category)
    )
    await callback.answer()


# ── Add category ──────────────────────────────────────────────────


@router.callback_query(F.data == "admin:cat:add")
async def cb_cat_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u2795 Введите название новой категории:"
    )
    await state.set_state(CategoryForm.name)
    await callback.answer()


@router.message(CategoryForm.name)
async def process_cat_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=name)
    await message.answer("Введите эмодзи для категории (или отправьте . чтобы пропустить):")
    await state.set_state(CategoryForm.emoji)


@router.message(CategoryForm.emoji)
async def process_cat_emoji(message: Message, state: FSMContext, session: AsyncSession) -> None:
    emoji = (message.text or "").strip()
    if emoji == ".":
        emoji = ""
    data = await state.get_data()
    category = await create_category(session, name=data["name"], emoji=emoji)
    await state.clear()
    await message.answer(
        f"\u2705 Категория «{category.emoji} {category.name}» создана.",
        reply_markup=admin_category_kb(category),
    )


# ── Edit category ─────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:cat:edit:"))
async def cb_cat_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    category_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    await state.update_data(category_id=category_id)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u270f\ufe0f Введите новое название категории:"
    )
    await state.set_state(CategoryEditForm.name)
    await callback.answer()


@router.message(CategoryEditForm.name)
async def process_cat_edit_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=name)
    await message.answer("Введите новый эмодзи (или . чтобы убрать):")
    await state.set_state(CategoryEditForm.emoji)


@router.message(CategoryEditForm.emoji)
async def process_cat_edit_emoji(message: Message, state: FSMContext, session: AsyncSession) -> None:
    emoji = (message.text or "").strip()
    if emoji == ".":
        emoji = ""
    data = await state.get_data()
    category = await update_category(session, data["category_id"], name=data["name"], emoji=emoji)
    await state.clear()
    if category is None:
        await message.answer("\u274c Категория не найдена.")
        return
    await message.answer(
        f"\u2705 Категория обновлена: «{category.emoji} {category.name}»",
        reply_markup=admin_category_kb(category),
    )


# ── Delete category ───────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:cat:delete:"))
async def cb_cat_delete(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    deleted = await delete_category(session, category_id)
    if not deleted:
        await callback.answer("Нельзя удалить: в категории есть товары", show_alert=True)
        return
    categories = await get_categories(session)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u2705 Категория удалена.\n\n\U0001f4e6 <b>Управление каталогом</b>",
        reply_markup=admin_categories_kb(categories),
    )
    await callback.answer()


# ── Products list ─────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:cat:products:"))
async def cb_category_products(callback: CallbackQuery, session: AsyncSession) -> None:
    category_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    category = await get_category(session, category_id)
    if category is None:
        await callback.answer("Категория не найдена")
        return
    products = await get_products_by_category(session, category_id)
    text = f"{category.emoji} <b>{category.name}</b> — товары:"
    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=admin_products_kb(products, category_id)
    )
    await callback.answer()


# ── Product card ──────────────────────────────────────────────────


@router.callback_query(F.data.regexp(r"^admin:prod:\d+$"))
async def cb_product_card(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":")[2])  # type: ignore[union-attr]
    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("Товар не найден")
        return
    text = f"<b>{product.name}</b>\n\n{product.description}\n\n\U0001f4b0 Цена: {product.price} \u20bd"
    await callback.message.edit_text(  # type: ignore[union-attr]
        text, reply_markup=admin_product_kb(product)
    )
    await callback.answer()


# ── Add product ───────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:prod:add:"))
async def cb_prod_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    category_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    await state.update_data(category_id=category_id)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u2795 Введите название товара:"
    )
    await state.set_state(ProductForm.name)
    await callback.answer()


@router.message(ProductForm.name)
async def process_prod_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=name)
    await message.answer("Введите описание товара:")
    await state.set_state(ProductForm.description)


@router.message(ProductForm.description)
async def process_prod_desc(message: Message, state: FSMContext) -> None:
    description = (message.text or "").strip()
    await state.update_data(description=description)
    await message.answer("Введите цену (целое число в рублях):")
    await state.set_state(ProductForm.price)


@router.message(ProductForm.price)
async def process_prod_price(message: Message, state: FSMContext, session: AsyncSession) -> None:
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Введите число:")
        return
    data = await state.get_data()
    product = await create_product(
        session,
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price=int(text),
    )
    await state.clear()
    await message.answer(
        f"\u2705 Товар «{product.name}» добавлен ({product.price} \u20bd).",
        reply_markup=admin_product_kb(product),
    )


# ── Edit product ──────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:prod:edit:"))
async def cb_prod_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    product_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u270f\ufe0f Введите новое название товара:"
    )
    await state.set_state(ProductEditForm.name)
    await callback.answer()


@router.message(ProductEditForm.name)
async def process_prod_edit_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Название слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(name=name)
    await message.answer("Введите новое описание:")
    await state.set_state(ProductEditForm.description)


@router.message(ProductEditForm.description)
async def process_prod_edit_desc(message: Message, state: FSMContext) -> None:
    description = (message.text or "").strip()
    await state.update_data(description=description)
    await message.answer("Введите новую цену (целое число в рублях):")
    await state.set_state(ProductEditForm.price)


@router.message(ProductEditForm.price)
async def process_prod_edit_price(message: Message, state: FSMContext, session: AsyncSession) -> None:
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Введите число:")
        return
    data = await state.get_data()
    product = await update_product(
        session,
        product_id=data["product_id"],
        name=data["name"],
        description=data["description"],
        price=int(text),
    )
    await state.clear()
    if product is None:
        await message.answer("\u274c Товар не найден.")
        return
    await message.answer(
        f"\u2705 Товар обновлён: «{product.name}» ({product.price} \u20bd)",
        reply_markup=admin_product_kb(product),
    )


# ── Delete product ────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:prod:delete:"))
async def cb_prod_delete(callback: CallbackQuery, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":")[3])  # type: ignore[union-attr]
    product = await get_product(session, product_id)
    if product is None:
        await callback.answer("Товар не найден")
        return
    category_id = product.category_id
    await delete_product(session, product_id)
    products = await get_products_by_category(session, category_id)
    await callback.message.edit_text(  # type: ignore[union-attr]
        "\u2705 Товар удалён.",
        reply_markup=admin_products_kb(products, category_id),
    )
    await callback.answer()
