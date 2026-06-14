import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from settings.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    path="/",
    response_model=list[CategoryRead],
)
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(select(Category))
        return result.scalars().all()
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
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Category).where(Category.id == category_id),
        )
        category = result.scalars().first()
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
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        new_category = Category(**category_data.model_dump())
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        return new_category
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
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Category).where(Category.id == category_id),
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        for field, value in category_update.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
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
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        result = await db.execute(
            select(Category).where(Category.id == category_id),
        )
        category = result.scalars().first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        await db.delete(category)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete category with id %d", category_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category",
        ) from exc
