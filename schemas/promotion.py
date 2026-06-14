from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PromotionCreate(BaseModel):
    store_id: int
    category_id: int
    title: str
    original_price: Decimal
    discounted_price: Decimal
    discount_percent: int
    image_path: Optional[str] = None
    starts_at: datetime
    ends_at: datetime


class PromotionUpdate(BaseModel):
    store_id: Optional[int] = None
    category_id: Optional[int] = None
    title: Optional[str] = None
    original_price: Optional[Decimal] = None
    discounted_price: Optional[Decimal] = None
    discount_percent: Optional[int] = None
    image_path: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class PromotionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    category_id: int
    title: str
    original_price: Decimal
    discounted_price: Decimal
    discount_percent: int
    image_path: Optional[str]
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime
