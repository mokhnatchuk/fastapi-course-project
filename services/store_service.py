from collections.abc import Sequence
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.store import Store
from schemas.store import StoreCreate, StoreUpdate
from settings.db import get_db


class StoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 50, offset: int = 0) -> Sequence[Store]:
        result = await self.db.execute(select(Store).limit(limit).offset(offset))
        return result.scalars().all()

    async def get_by_id(self, store_id: int) -> Store | None:
        result = await self.db.execute(
            select(Store).where(Store.id == store_id),
        )
        return result.scalars().first()

    async def create(self, data: StoreCreate) -> Store:
        new_store = Store(**data.model_dump())
        self.db.add(new_store)
        await self.db.commit()
        await self.db.refresh(new_store)
        return new_store

    async def update(
        self,
        store_id: int,
        data: StoreUpdate,
    ) -> Store | None:
        store = await self.get_by_id(store_id)
        if not store:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(store, field, value)

        self.db.add(store)
        await self.db.commit()
        await self.db.refresh(store)
        return store

    async def delete(self, store_id: int) -> bool:
        store = await self.get_by_id(store_id)
        if not store:
            return False

        await self.db.delete(store)
        await self.db.commit()
        return True


async def get_store_service(
    db: AsyncSession = Depends(get_db),
) -> StoreService:
    return StoreService(db)
