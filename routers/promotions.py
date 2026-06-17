import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.promotion import PromotionCreate, PromotionRead, PromotionUpdate
from services.promotion_service import PromotionService, get_promotion_service
from fastapi.responses import FileResponse
from services.pdf_generator import generate_promotions_report
from authx import RequestToken
from services.user_service import UserService, get_user_service
from utils.security import security

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.get(
    path="/",
    response_model=list[PromotionRead],
)
async def get_promotions(
    limit: int = 50,
    offset: int = 0,
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        return await promotion_service.get_all(limit=limit, offset=offset)
    except Exception as exc:
        logger.exception("Failed to get promotions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get promotions",
        ) from exc


@router.get(
    path="/report",
    summary="Generate PDF report of all promotions",
)
async def get_promotions_report(
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    try:
        promotions = await promotion_service.get_all_unpaginated()
        filepath = generate_promotions_report(promotions)
        return FileResponse(
            path=filepath,
            filename="promotions_report.pdf",
            media_type="application/pdf",
        )
    except Exception as exc:
        logger.exception("Failed to generate promotions report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
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
    token: RequestToken = Depends(security.access_token_required),
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
    user_service: UserService = Depends(get_user_service),
    token: RequestToken = Depends(security.access_token_required),
):
    try:
        current_user = await user_service.get_by_id(
            user_id=int(token.sub),  # pyright: ignore[reportAttributeAccessIssue]
        )
        if not current_user or current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete promotions",
            )

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
