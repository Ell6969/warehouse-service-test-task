import uuid
from typing import List

from src.dao.base_dao import MovementDAO
from src.db.schemas import SGetMovementByIdResult, SMovementAll, SMovementStat
from src.enums import EventType


class MovementService:

    @classmethod
    async def get_movements_by_id(cls, movement_id: uuid.UUID) -> SGetMovementByIdResult:
        moves: List[SMovementAll] = await MovementDAO.find_all(movement_id=movement_id)
        departure = None
        arrival = None

        for m in moves:
            if m.event_type == EventType.departure:
                departure = m
            elif m.event_type == EventType.arrival:
                arrival = m

        stats = None
        if departure and arrival:
            stats = SMovementStat(
                sender_warehouse=departure.warehouse_id,
                recipient_warehouse=arrival.warehouse_id,
                time_diff=str(arrival.timestamp - departure.timestamp),
                diff_in_quantity=arrival.quantity - departure.quantity,
            )

        return SGetMovementByIdResult(movements=moves, stats=stats)
