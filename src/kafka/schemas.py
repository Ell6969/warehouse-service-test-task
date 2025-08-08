import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.enums import EventType
from src.kafka.constants import KafkaConstant


class SKafkaMessageData(BaseModel):
    movement_id: uuid.UUID
    warehouse_id: uuid.UUID
    timestamp: datetime
    event: EventType
    product_id: uuid.UUID
    quantity: int = Field(ge=0)

    model_config = {"from_attributes": True}


class SKafkaMessageAll(BaseModel):
    id: uuid.UUID
    source: str = Field(..., pattern=KafkaConstant.PATTERN_FOR_SOURCE_FIELD)
    specversion: str
    type: str
    datacontenttype: str
    dataschema: str
    time: int
    subject: str
    destination: str
    data: SKafkaMessageData

    model_config = {"from_attributes": True}
