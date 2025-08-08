import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.db.database import async_session_maker
from src.db.models import Movement, Product, StockItem, Warehouse
from src.db.schemas import (
    SMovementAll,
    SProductAll,
    SStockItemAll,
    SStockItemUpdate,
    SWarehouseAll,
)
from src.dependencies import SFilterPagination
from src.enums import EventType

logger = logging.getLogger(__name__)


class BaseDAO:
    model = None
    schema_all_fields = None

    @classmethod
    async def find_all(cls, pagination: SFilterPagination = SFilterPagination(), **filter_by):
        """
        Находит и возвращает все записи. С возможным фильтром и пагинацией.
        :param filter_by: Фильтры для поиска записи.
        :return: Список объектов schema_all_fields.
        """
        try:
            async with async_session_maker() as session:
                query = (
                    select(cls.model)
                    .filter_by(**filter_by)
                    .limit(pagination.page_size)
                    .offset((pagination.page - 1) * pagination.page_size)
                )
                result = await session.execute(query)
                instances = result.scalars().all()
                return [cls.schema_all_fields.model_validate(instance) for instance in instances]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных при добавлении записи. {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка при добавлении записи.{e}")

    @classmethod
    async def add(cls, db_session_for_transaction=None, **data):
        """
        Добавляет запись в таблицу.
        :param data: Словарь с данными для добавления.
        :return: Сам объект schema_all_fields
        """
        session = db_session_for_transaction
        try:
            instance = cls.model(**data)
            if session is None:
                async with async_session_maker() as session:
                    session.add(instance)
                    await session.commit()
                    await session.refresh(instance)
            else:
                session.add(instance)

            return cls.schema_all_fields.model_validate(instance)
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных при добавлении записи. {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка при добавлении записи.{e}")

    @classmethod
    async def find_one_or_none(cls, db_session_for_transaction=None, **filter_by):
        """
        Находит и возвращает одну запись по фильтру.
        :param filter_by: Фильтры для поиска записи.
        :return: Сам объект schema_all_fields.
        """
        query = select(cls.model).filter_by(**filter_by)
        result = None
        if db_session_for_transaction is None:
            async with async_session_maker() as session:
                result = await session.execute(query)
        else:
            result = await db_session_for_transaction.execute(query)

        instance = result.scalars().one_or_none()

        if instance:
            try:
                return cls.schema_all_fields.model_validate(instance)
            except Exception as e:
                raise e

        return None

    @classmethod
    async def find_one_or_create(cls, db_session_for_transaction=None, defaults=None, **filter_by):
        """
        Ищет одну запись по фильтру или создает новую, если не найдена.
        :param defaults: Словарь с данными для создания, если запись не найдена.
        :param filter_by: Фильтры для поиска записи.
        :return: Сам объект schema_all_fields.
        :example: record = await BaseDAO.find_one_or_create(defaults={"name": "Example"}, name="Example")
        """
        defaults = defaults or {}

        try:
            existing_record = await cls.find_one_or_none(
                db_session_for_transaction=db_session_for_transaction, **filter_by
            )

            if existing_record:
                return cls.schema_all_fields.model_validate(existing_record)

            new_record = await cls.add(db_session_for_transaction=db_session_for_transaction, **defaults)
            return new_record

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка базы данных при добавлении записи. {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка при добавлении записи.{e}")


class WarehouseDAO(BaseDAO):
    model = Warehouse
    schema_all_fields = SWarehouseAll


class ProductDAO(BaseDAO):
    model = Product
    schema_all_fields = SProductAll


class StockItemDAO(BaseDAO):
    model = StockItem
    schema_all_fields = SStockItemAll

    @classmethod
    async def find_one_or_create_or_update_quantity(
        cls,
        db_session_for_transaction,
        data: SStockItemUpdate,
    ) -> SStockItemAll:
        """
        Обновляет количество товара на складе, либо создаёт запись.
        :param warehouse_id: ID склада
        :param product_id: ID товара
        :param quantity: Изменение количества (из Kafka)
        :param event_type: arrival или departure
        :return: Объект SStockItemAll
        """
        session = db_session_for_transaction
        try:
            stmt = (
                select(cls.model)
                .where(cls.model.warehouse_id == data.warehouse_id, cls.model.product_id == data.product_id)
                .with_for_update()
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                cls._update_quantity(existing, data.quantity, data.event_type)
                await session.flush()
                return cls.schema_all_fields.model_validate(existing)

            # Если нет записи — создаём новую
            initial_quantity = data.quantity if data.event_type == EventType.arrival else 0
            if data.event_type == EventType.departure and data.quantity > 0:
                logger.warning(
                    f"Попытка ухода товара с пустого склада: "
                    f"product_id={data.product_id}, warehouse_id={data.warehouse_id}, quantity={data.quantity}"
                )

            instance = cls.model(
                warehouse_id=data.warehouse_id,
                product_id=data.product_id,
                quantity=initial_quantity,
            )
            session.add(instance)
            await session.flush()
            return cls.schema_all_fields.model_validate(instance)

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка БД при изменении stock_item: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка при обновлении stock_item: {e}")

    @classmethod
    def _update_quantity(cls, existing: StockItem, quantity: int, event_type: EventType):
        if event_type == EventType.arrival:
            existing.quantity += quantity
        elif event_type == EventType.departure:
            if existing.quantity - quantity < 0:
                logger.warning(
                    f"Уход товара превысит остаток: "
                    f"{existing.quantity} - {quantity} < 0 "
                    f"(product_id={existing.product_id}, warehouse_id={existing.warehouse_id})"
                )
            existing.quantity = max(0, existing.quantity - quantity)


class MovementDAO(BaseDAO):
    model = Movement
    schema_all_fields = SMovementAll
