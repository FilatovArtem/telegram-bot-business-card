import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repositories import (
    create_category,
    create_product,
    delete_category,
    get_categories,
    get_product,
)


@pytest.mark.asyncio
async def test_create_and_get_categories_roundtrip(session: AsyncSession) -> None:
    await create_category(session, name="Торты", emoji="🎂")
    await create_category(session, name="Капкейки", emoji="🧁")

    categories = await get_categories(session)

    assert len(categories) == 2
    names = {c.name for c in categories}
    assert "Торты" in names
    assert "Капкейки" in names


@pytest.mark.asyncio
async def test_get_categories_eager_loads_products(session: AsyncSession) -> None:
    cat = await create_category(session, name="Торты", emoji="🎂")
    await create_product(session, category_id=cat.id, name="Медовик", description="Вкусный", price=2500)

    categories = await get_categories(session)

    # Access .products outside session — must not raise MissingGreenlet (eager loaded)
    assert len(categories[0].products) == 1
    assert categories[0].products[0].name == "Медовик"


@pytest.mark.asyncio
async def test_delete_category_with_products_returns_false(session: AsyncSession) -> None:
    cat = await create_category(session, name="Торты", emoji="🎂")
    await create_product(session, category_id=cat.id, name="Медовик", description="", price=1000)

    result = await delete_category(session, cat.id)

    assert result is False


@pytest.mark.asyncio
async def test_delete_empty_category_succeeds(session: AsyncSession) -> None:
    cat = await create_category(session, name="Пустая категория", emoji="")

    result = await delete_category(session, cat.id)

    assert result is True
    # Verify it's gone
    categories = await get_categories(session)
    assert len(categories) == 0


@pytest.mark.asyncio
async def test_create_and_get_product(session: AsyncSession) -> None:
    cat = await create_category(session, name="Торты", emoji="🎂")
    product = await create_product(
        session,
        category_id=cat.id,
        name="Медовик",
        description="1.5 кг",
        price=2500,
    )

    fetched = await get_product(session, product.id)

    assert fetched is not None
    assert fetched.name == "Медовик"
    assert fetched.price == 2500
    assert fetched.category_id == cat.id
