from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .category import Category
    from .store import Store


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    original_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    discounted_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    discount_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        onupdate=datetime.now,
    )

    store: Mapped[Store] = relationship(back_populates="promotions")
    category: Mapped[Category] = relationship(back_populates="promotions")
