import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.promotion import Promotion
from schemas.promotion import PromotionCreate, PromotionRead, PromotionUpdate
from settings.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.get(
    path="/",
    response_model=list[PromotionRead],
)
async def get_promotions(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(select(Promotion))
        return result.scalars().all()
    except Exception as exc:
        logger.exception("Failed to get promotions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get promotions",
        ) from exc


@router.get(
    path="/{promotion_id}",
    response_model=PromotionRead,
)
async def get_promotion(
    promotion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Promotion).where(Promotion.id == promotion_id),
        )
        promotion = result.scalars().first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        return promotion
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get promotion with id %d", promotion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get promotion",
        ) from exc


@router.post(
    path="/",
    response_model=PromotionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_promotion(
    promotion_data: PromotionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        new_promotion = Promotion(**promotion_data.model_dump())
        db.add(new_promotion)
        await db.commit()
        await db.refresh(new_promotion)
        return new_promotion
    except Exception as exc:
        logger.exception("Failed to create promotion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create promotion",
        ) from exc


@router.put(
    path="/{promotion_id}",
    response_model=PromotionRead,
)
async def update_promotion(
    promotion_id: int,
    promotion_update: PromotionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Promotion).where(Promotion.id == promotion_id),
        )
        promotion = result.scalars().first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )

        for field, value in promotion_update.model_dump(exclude_unset=True).items():
            setattr(promotion, field, value)

        await db.commit()
        await db.refresh(promotion)
        return promotion
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update promotion with id %d", promotion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update promotion",
        ) from exc


@router.delete(
    path="/{promotion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_promotion(
    promotion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Promotion).where(Promotion.id == promotion_id),
        )
        promotion = result.scalars().first()
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )

        await db.delete(promotion)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete promotion with id %d", promotion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete promotion",
        ) from exc
