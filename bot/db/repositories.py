from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import Booking, Category, Product, User

# ── Users ──────────────────────────────────────────────────────────


async def upsert_user(
    session: AsyncSession,
    user_id: int,
    full_name: str,
    username: str | None,
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        user = User(id=user_id, full_name=full_name, username=username)
        session.add(user)
    else:
        user.full_name = full_name
        user.username = username
    await session.commit()
    return user


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(select(User.id))
    return [row[0] for row in result.all()]


async def count_users(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(User.id)))
    return result.scalar_one()


# ── Catalog ────────────────────────────────────────────────────────


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category).options(selectinload(Category.products)).order_by(Category.id)
    )
    return list(result.scalars().all())


async def get_products_by_category(session: AsyncSession, category_id: int) -> list[Product]:
    result = await session.execute(
        select(Product).where(Product.category_id == category_id).order_by(Product.id)
    )
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


# ── Bookings ───────────────────────────────────────────────────────


async def create_booking(
    session: AsyncSession,
    user_id: int,
    service: str,
    client_name: str,
    phone: str,
    desired_date: str,
) -> Booking:
    booking = Booking(
        user_id=user_id,
        service=service,
        client_name=client_name,
        phone=phone,
        desired_date=desired_date,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


async def get_recent_bookings(session: AsyncSession, limit: int = 10) -> list[Booking]:
    result = await session.execute(select(Booking).order_by(Booking.created_at.desc()).limit(limit))
    return list(result.scalars().all())


async def get_booking(session: AsyncSession, booking_id: int) -> Booking | None:
    return await session.get(Booking, booking_id)


async def get_bookings_by_status(session: AsyncSession, status: str) -> list[Booking]:
    result = await session.execute(
        select(Booking).where(Booking.status == status).order_by(Booking.created_at.desc())
    )
    return list(result.scalars().all())


async def update_booking_status(session: AsyncSession, booking_id: int, status: str) -> Booking | None:
    booking = await session.get(Booking, booking_id)
    if booking is None:
        return None
    booking.status = status
    await session.commit()
    return booking


# ── Catalog management ─────────────────────────────────────────────


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def create_category(session: AsyncSession, name: str, emoji: str = "") -> Category:
    category = Category(name=name, emoji=emoji)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(session: AsyncSession, category_id: int, name: str, emoji: str) -> Category | None:
    category = await session.get(Category, category_id)
    if category is None:
        return None
    category.name = name
    category.emoji = emoji
    await session.commit()
    return category


async def delete_category(session: AsyncSession, category_id: int) -> bool:
    category = await session.get(Category, category_id)
    if category is None:
        return False
    products = await get_products_by_category(session, category_id)
    if products:
        return False
    await session.delete(category)
    await session.commit()
    return True


async def create_product(
    session: AsyncSession,
    category_id: int,
    name: str,
    description: str,
    price: int,
) -> Product:
    product = Product(category_id=category_id, name=name, description=description, price=price)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def update_product(
    session: AsyncSession,
    product_id: int,
    name: str,
    description: str,
    price: int,
) -> Product | None:
    product = await session.get(Product, product_id)
    if product is None:
        return None
    product.name = name
    product.description = description
    product.price = price
    await session.commit()
    return product


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    product = await session.get(Product, product_id)
    if product is None:
        return False
    await session.delete(product)
    await session.commit()
    return True


async def count_bookings(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(Booking.id)))
    return result.scalar_one()
