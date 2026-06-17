import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from services.category_service import CategoryService, get_category_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    path="/",
    response_model=list[CategoryRead],
)
async def get_categories(
    limit: int = 50,
    offset: int = 0,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        return await category_service.get_all(limit=limit, offset=offset)
    except Exception as exc:
        logger.exception("Failed to get categories")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get categories",
        ) from exc


@router.get(
    path="/{category_id}",
    response_model=CategoryRead,
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        category = await category_service.get_by_id(category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return category
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get category with id %d", category_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category",
        ) from exc


@router.post(
    path="/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        return await category_service.create(data=category_data)
    except Exception as exc:
        logger.exception("Failed to create category")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category",
        ) from exc


@router.put(
    path="/{category_id}",
    response_model=CategoryRead,
)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        category = await category_service.update(
            category_id=category_id,
            data=category_update,
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return category
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update category with id %d", category_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category",
        ) from exc


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        deleted = await category_service.delete(category_id=category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete category with id %d", category_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category",
        ) from exc
