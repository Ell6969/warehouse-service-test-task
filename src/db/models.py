import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.constant import ModelFieldConstant
from src.db.database import Base
from src.enums import EventType


class Warehouse(Base):
    __tablename__ = "warehouse"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(ModelFieldConstant.WH_CODE))


class Product(Base):
    __tablename__ = "product"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)


class StockItem(Base):
    __tablename__ = "stock_item"
    __table_args__ = (CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),)

    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("warehouse.id"), primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=0)


class Movement(Base):
    __tablename__ = "movement"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        UniqueConstraint("movement_id", "event_type", name="uq_movement_id_event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    movement_id: Mapped[uuid.UUID] = mapped_column()
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quantity: Mapped[int] = mapped_column(default=0)
    event_type: Mapped[EventType] = mapped_column(ENUM(EventType))

    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
