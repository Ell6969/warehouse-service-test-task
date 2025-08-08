import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.enums import EventType
from src.kafka.constants import KafkaConstant


class SIdUUIDMixin(BaseModel):
    id: uuid.UUID

    model_config = {"from_attributes": True}


class SWarehouseIdUUIDMixin(BaseModel):
    warehouse_id: uuid.UUID

    model_config = {"from_attributes": True}


class SProductIdUUIDMixin(BaseModel):
    product_id: uuid.UUID

    model_config = {"from_attributes": True}


class SQuantityMixin(BaseModel):
    quantity: int = 0

    model_config = {"from_attributes": True}


class SEventTypeMixin(BaseModel):
    event_type: EventType

    model_config = {"from_attributes": True}


class SMovementIdMixin(BaseModel):
    movement_id: uuid.UUID

    model_config = {"from_attributes": True}


class SProductAll(SIdUUIDMixin):
    model_config = {"from_attributes": True}


class SWarehouseAll(SIdUUIDMixin):
    code: str = Field(..., pattern=KafkaConstant.PATTERN_FOR_SOURCE_FIELD)

    model_config = {"from_attributes": True}


class SStockItemAll(SWarehouseIdUUIDMixin, SProductIdUUIDMixin, SQuantityMixin):
    model_config = {"from_attributes": True}


class SStockItemUpdate(SWarehouseIdUUIDMixin, SProductIdUUIDMixin, SQuantityMixin, SEventTypeMixin):
    model_config = {"from_attributes": True}


class SMovementAll(SMovementIdMixin, SWarehouseIdUUIDMixin, SProductIdUUIDMixin, SQuantityMixin, SEventTypeMixin):
    id: int | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class SMovementStat(BaseModel):
    sender_warehouse: uuid.UUID
    recipient_warehouse: uuid.UUID
    time_diff: str
    diff_in_quantity: int

    model_config = {"from_attributes": True}


class SGetMovementByIdResult(BaseModel):
    movements: List[SMovementAll] = []
    stats: SMovementStat | None = None

    model_config = {"from_attributes": True}


class SGetProductWarehouseByIdResult(BaseModel):
    product_quantity: int = Field(0, ge=0)

    model_config = {"from_attributes": True}
