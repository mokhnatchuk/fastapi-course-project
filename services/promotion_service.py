from collections.abc import Sequence
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.promotion import Promotion
from schemas.promotion import PromotionCreate, PromotionUpdate
from settings.db import get_db


class PromotionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 50, offset: int = 0) -> Sequence[Promotion]:
        result = await self.db.execute(select(Promotion).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_all_unpaginated(self) -> Sequence[Promotion]:
        result = await self.db.execute(select(Promotion))
        return result.scalars().all()

    async def get_by_id(self, promotion_id: int) -> Promotion | None:
        result = await self.db.execute(
            select(Promotion).where(Promotion.id == promotion_id),
        )
        return result.scalars().first()

    async def create(self, data: PromotionCreate) -> Promotion:
        new_promotion = Promotion(**data.model_dump())
        self.db.add(new_promotion)
        await self.db.commit()
        await self.db.refresh(new_promotion)
        return new_promotion

    async def update(
        self,
        promotion_id: int,
        data: PromotionUpdate,
    ) -> Promotion | None:
        promotion = await self.get_by_id(promotion_id)
        if not promotion:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(promotion, field, value)

        self.db.add(promotion)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def delete(self, promotion_id: int) -> bool:
        promotion = await self.get_by_id(promotion_id)
        if not promotion:
            return False

        await self.db.delete(promotion)
        await self.db.commit()
        return True


async def get_promotion_service(
    db: AsyncSession = Depends(get_db),
) -> PromotionService:
    return PromotionService(db)
