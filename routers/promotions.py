import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.promotion import PromotionCreate, PromotionRead, PromotionUpdate
from services.promotion_service import PromotionService, get_promotion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.get(
    path="/",
    response_model=list[PromotionRead],
)
async def get_promotions(
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        return await promotion_service.get_all()
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
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        promotion = await promotion_service.get_by_id(
            promotion_id=promotion_id,
        )
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
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        return await promotion_service.create(data=promotion_data)
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
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        promotion = await promotion_service.update(
            promotion_id=promotion_id,
            data=promotion_update,
        )
        if not promotion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
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
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        deleted = await promotion_service.delete(promotion_id=promotion_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete promotion with id %d", promotion_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete promotion",
        ) from exc
