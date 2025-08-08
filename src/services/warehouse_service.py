import uuid

from src.dao.base_dao import StockItemDAO
from src.db.schemas import SGetProductWarehouseByIdResult, SStockItemAll


class WarehouseService:

    @classmethod
    async def get_product_warehouse_by_id(
        cls, warehouse_id: uuid.UUID, product_id: uuid.UUID
    ) -> SGetProductWarehouseByIdResult:

        stock_item: SStockItemAll | None = await StockItemDAO.find_one_or_none(
            warehouse_id=warehouse_id,
            product_id=product_id,
        )
        return SGetProductWarehouseByIdResult(product_quantity=stock_item.quantity if stock_item else None)
