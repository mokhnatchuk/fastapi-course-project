import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.store import Store
from schemas.store import StoreCreate, StoreRead, StoreUpdate
from settings.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get(
    path="/",
    response_model=list[StoreRead],
)
async def get_stores(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(select(Store))
        return result.scalars().all()
    except Exception as exc:
        logger.exception("Failed to get stores")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get stores",
        ) from exc


@router.get(
    path="/{store_id}",
    response_model=StoreRead,
)
async def get_store(
    store_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Store).where(Store.id == store_id),
        )
        store = result.scalars().first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found",
            )
        return store
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get store with id %d", store_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get store",
        ) from exc


@router.post(
    path="/",
    response_model=StoreRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_store(
    store_data: StoreCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        new_store = Store(**store_data.model_dump())
        db.add(new_store)
        await db.commit()
        await db.refresh(new_store)
        return new_store
    except Exception as exc:
        logger.exception("Failed to create store")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create store",
        ) from exc


@router.put(
    path="/{store_id}",
    response_model=StoreRead,
)
async def update_store(
    store_id: int,
    store_update: StoreUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Store).where(Store.id == store_id),
        )
        store = result.scalars().first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found",
            )

        for field, value in store_update.model_dump(exclude_unset=True).items():
            setattr(store, field, value)

        await db.commit()
        await db.refresh(store)
        return store
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update store with id %d", store_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update store",
        ) from exc


@router.delete(
    path="/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_store(
    store_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Store).where(Store.id == store_id),
        )
        store = result.scalars().first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found",
            )

        await db.delete(store)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete store with id %d", store_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete store",
        ) from exc
