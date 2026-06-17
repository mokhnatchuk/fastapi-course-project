import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.store import StoreCreate, StoreRead, StoreUpdate
from services.store_service import StoreService, get_store_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get(
    path="/",
    response_model=list[StoreRead],
)
async def get_stores(
    limit: int = 50,
    offset: int = 0,
    store_service: StoreService = Depends(get_store_service),
):
    try:
        return await store_service.get_all(limit=limit, offset=offset)
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
    store_service: StoreService = Depends(get_store_service),
):
    try:
        store = await store_service.get_by_id(store_id=store_id)
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
    store_service: StoreService = Depends(get_store_service),
):
    try:
        return await store_service.create(data=store_data)
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
    store_service: StoreService = Depends(get_store_service),
):
    try:
        store = await store_service.update(
            store_id=store_id,
            data=store_update,
        )
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found",
            )
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
    store_service: StoreService = Depends(get_store_service),
):
    try:
        deleted = await store_service.delete(store_id=store_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete store with id %d", store_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete store",
        ) from exc
