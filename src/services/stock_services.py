from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from src.dao.base_dao import MovementDAO, ProductDAO, StockItemDAO, WarehouseDAO
from src.db.database import async_session_maker
from src.db.schemas import SStockItemUpdate
from src.kafka.schemas import SKafkaMessageAll
from src.redis.service import redis_service


class StockService:

    @classmethod
    async def processing_message(cls, data: SKafkaMessageAll):
        async with async_session_maker() as session:
            try:
                async with session.begin():

                    await WarehouseDAO.find_one_or_create(
                        db_session_for_transaction=session,
                        defaults={
                            "id": data.data.warehouse_id,
                            "code": data.source,
                        },
                        id=data.data.warehouse_id,
                    )
                    await ProductDAO.find_one_or_create(
                        db_session_for_transaction=session,
                        defaults={
                            "id": data.data.product_id,
                        },
                        id=data.data.product_id,
                    )
                    await MovementDAO.find_one_or_create(
                        db_session_for_transaction=session,
                        defaults={
                            "movement_id": data.data.movement_id,
                            "warehouse_id": data.data.warehouse_id,
                            "timestamp": data.data.timestamp,
                            "quantity": data.data.quantity,
                            "event_type": data.data.event,
                            "product_id": data.data.product_id,
                        },
                        movement_id=data.data.movement_id,
                        event_type=data.data.event,
                    )
                    await StockItemDAO.find_one_or_create_or_update_quantity(
                        db_session_for_transaction=session,
                        data=SStockItemUpdate(
                            event_type=data.data.event,
                            quantity=data.data.quantity,
                            product_id=data.data.product_id,
                            warehouse_id=data.data.warehouse_id,
                        ),
                    )
                    await redis_service.clear_cache_by_path_params(
                        warehouse_id=str(data.data.warehouse_id),
                        product_id=str(data.data.product_id)
                    )
                    await redis_service.clear_cache_by_path_params(
                        movement_id=str(data.data.movement_id)
                    )

            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Неизвестная ошибка: {e}")
