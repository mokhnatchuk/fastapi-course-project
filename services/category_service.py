from collections.abc import Sequence
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate
from settings.db import get_db


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 50, offset: int = 0) -> Sequence[Category]:
        result = await self.db.execute(select(Category).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id),
        )
        return result.scalars().first()

    async def create(self, data: CategoryCreate) -> Category:
        new_category = Category(**data.model_dump())
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        return new_category

    async def update(
        self,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category | None:
        category = await self.get_by_id(category_id)
        if not category:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        category = await self.get_by_id(category_id)
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        return True


async def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:
    return CategoryService(db)
