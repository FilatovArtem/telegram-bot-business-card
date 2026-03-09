import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Category, Product


async def seed_catalog(session: AsyncSession, seed_path: str = "data/seed.json") -> None:
    """Load demo catalog data from JSON if DB is empty."""
    result = await session.execute(select(Category).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # already seeded

    path = Path(seed_path)
    if not path.exists():
        return

    data = json.loads(path.read_text(encoding="utf-8"))

    for cat_data in data["categories"]:
        category = Category(
            id=cat_data["id"],
            name=cat_data["name"],
            emoji=cat_data.get("emoji", ""),
        )
        session.add(category)
        await session.flush()

        for prod_data in cat_data["products"]:
            product = Product(
                category_id=category.id,
                name=prod_data["name"],
                description=prod_data.get("description", ""),
                price=prod_data.get("price", 0),
                image_url=prod_data.get("image_url"),
            )
            session.add(product)

    await session.commit()
