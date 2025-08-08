from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class SFilterPagination(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы для пагинации")
    page_size: int = Field(20, ge=1, le=100, description="Количество элементов на странице, максимум 100")


PaginationDep = Annotated[SFilterPagination, Depends(SFilterPagination)]
