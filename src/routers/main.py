from uuid import UUID

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.redis.utils import path_param_key_builder
from src.services.movement_service import MovementService, SGetMovementByIdResult
from src.services.warehouse_service import (
    SGetProductWarehouseByIdResult,
    WarehouseService,
)

router = APIRouter(prefix="", tags=["API"])


@router.get("/movements/{movement_id}")
@cache(expire=100, key_builder=path_param_key_builder)
async def get_movement(movement_id: UUID) -> SGetMovementByIdResult:
    """
    Возвращает информацию о перемещении по его ID, включая отправителя, получателя, время, прошедшее между отправкой и приемкой, и разницу в количестве товара.
    """
    import asyncio

    # тест кэш
    await asyncio.sleep(5)
    return await MovementService.get_movements_by_id(movement_id)


@router.get("/warehouses/{warehouse_id}/products/{product_id}")
@cache(expire=100, key_builder=path_param_key_builder)
async def get_remains_product_warehouse(warehouse_id: UUID, product_id: UUID) -> SGetProductWarehouseByIdResult:
    """
    Возвращает информацию текущем запасе товара в конкретном складе.
    """
    import asyncio

    # тест кэш
    await asyncio.sleep(5)
    return await WarehouseService.get_product_warehouse_by_id(warehouse_id, product_id)
