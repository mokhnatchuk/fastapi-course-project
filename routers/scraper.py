import logging
from authx import RequestToken
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.silpo_scraper import SilpoScraper
from services.user_service import UserService, get_user_service
from settings.db import get_db
from utils.security import security

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["Scraper"])


@router.post(
    path="/silpo",
    summary="Scrape promotions from Silpo API",
)
async def scrape_silpo(
    db: AsyncSession = Depends(get_db),
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
                detail="Only admins can run scraper",
            )

        scraper = SilpoScraper(db)
        try:
            result = await scraper.scrape()
        finally:
            await scraper.close()

        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to scrape Silpo")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scrape Silpo",
        ) from exc
