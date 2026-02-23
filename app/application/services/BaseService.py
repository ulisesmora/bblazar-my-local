import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from app.domain.repositories.repositories import IBaseRepository
from app.domain.services.service import IService

ModelType = TypeVar("ModelType")

class BaseService(IService[ModelType], Generic[ModelType]):
    """
    Implementación genérica de IService.
    Esta clase maneja la lógica CRUD básica delegando en un repositorio.
    """
    def __init__(self, repository: IBaseRepository[ModelType]):
        self.repository = repository

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        return await self.repository.get(id)

    async def list_all(self) -> Sequence[ModelType] | None:
        return await self.repository.list_all()

    async def create(self, data: Any) -> ModelType:
        return await self.repository.create(data)

    async def update(self, id: uuid.UUID, data: Any) -> ModelType:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            raise ValueError("Registro no encontrado")
        return await self.repository.update(db_obj, data)

    async def delete(self, id: uuid.UUID) -> bool:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            raise ValueError("Registro no encontrado")
        return await self.repository.delete(id)