import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.domain.models.models import KnowledgeSource
from app.infrastructure.repositories.base import BaseRepository


class KnowledgeService(BaseService[KnowledgeSource]):
    """
    Servicio para la Base de Conocimiento (RAG) del Asistente Virtual.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.knowledge_repo = BaseRepository(KnowledgeSource, db)
        super().__init__(self.knowledge_repo)

    async def get_business_sources(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[KnowledgeSource]:
        statement = select(KnowledgeSource).where(KnowledgeSource.business_id == business_id)
        
        if active_only:
            statement = statement.where(KnowledgeSource.is_active == True)
            
        statement = statement.order_by(col(KnowledgeSource.created_at).desc())
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def mark_as_indexed(self, source_id: uuid.UUID) -> KnowledgeSource:
        """Actualiza la fecha de última indexación (cuando el bot MCP termina de leerlo)."""
        source = await self.knowledge_repo.get(source_id)
        if not source:
            raise ValueError("Documento no encontrado.")
        return await self.knowledge_repo.update(source, {"last_indexed_at": datetime.utcnow()})