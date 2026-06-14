from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class StoreCreate(BaseModel):
    name: str
    slug: str


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class StoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    created_at: datetime
