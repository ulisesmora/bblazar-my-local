import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from app.domain.repositories.repositories import IBaseRepository

# Definimos el TypeVar para asegurar compatibilidad con Python 3.10 y 3.11
ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(IBaseRepository[ModelType], Generic[ModelType]):  # noqa: UP046
    """
    Abstracción genérica para operaciones CRUD comunes.
    Compatible con Python 3.10+ (PEP 484).
    """
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> ModelType | None:
        return await self.db.get(self.model, id)
    
    async def list_all(self) -> Sequence[ModelType] | None:
        statement = select(self.model)
        # 2. Ejecutamos la sentencia en la base de datos
        result = await self.db.execute(statement)
        # 3. Retornamos los resultados como una lista (scalars)
        return result.scalars().all()
    
    
    async def create(self, obj_in: ModelType) -> ModelType:
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in
    
    
    async def update(
        self, 
        db_obj: ModelType, 
        obj_in: ModelType | dict[str, Any] | BaseModel
    ) -> ModelType:
        """
        Actualiza un registro existente de forma parcial o total.
        Acepta un diccionario de cambios o un esquema de validación.
        """
        # Convertimos el objeto de entrada a diccionario si es un modelo
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True evita sobreescribir con Nones campos no enviados
            update_data = obj_in.model_dump(exclude_unset=True)

        # Aplicamos los cambios al objeto de la base de datos
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: uuid.UUID) -> bool:
        obj = await self.get(id)
        if obj:
            # Implementamos Soft Delete si el modelo tiene el atributo deleted_at
            if hasattr(obj, "deleted_at"):
                obj.deleted_at = datetime.utcnow()
                self.db.add(obj)
            else:
                await self.db.delete(obj)
            await self.db.commit()
            return True
        return False