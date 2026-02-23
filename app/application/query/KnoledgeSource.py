import uuid
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.KnowledgeService import KnowledgeService
from app.domain.models.models import KnowledgeSource


class KnowledgeQueries:
    def __init__(self, db: AsyncSession):
        self.service = KnowledgeService(db)

    async def get_source(self, source_id: uuid.UUID) -> KnowledgeSource:
        source = await self.service.get_by_id(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Fuente de conocimiento no encontrada.")
        return source

    async def get_business_knowledge(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[KnowledgeSource]:
        return await self.service.get_business_sources(business_id, active_only)