import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.KnowledgeService import KnowledgeService
from app.domain.models.models import KnowledgeSource
from app.domain.schemas.knowledge import KnowledgeSourceCreate, KnowledgeSourceUpdate


class KnowledgeCommands:
    def __init__(self, db: AsyncSession):
        self.service = KnowledgeService(db)

    async def add_source(self, data: KnowledgeSourceCreate) -> KnowledgeSource:
        new_source = KnowledgeSource(**data.model_dump())
        return await self.service.create(new_source)

    async def update_source(self, source_id: uuid.UUID, data: KnowledgeSourceUpdate) -> KnowledgeSource:
        update_dict = data.model_dump(exclude_unset=True)
        try:
            return await self.service.update(source_id, update_dict)
        except ValueError:
            raise HTTPException(status_code=404, detail="Fuente de conocimiento no encontrada.")

    async def set_indexed(self, source_id: uuid.UUID) -> KnowledgeSource:
        """Marca el documento como leído por la IA."""
        try:
            return await self.service.mark_as_indexed(source_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Fuente no encontrada.")

    async def delete_source(self, source_id: uuid.UUID) -> bool:
        try:
            return await self.service.delete(source_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Fuente no encontrada.")