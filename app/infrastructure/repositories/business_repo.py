import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.domain.models.models import Business
from app.domain.repositories.repositories import IBusinessRepository
from app.infrastructure.repositories.base import BaseRepository


class BusinessRepository(BaseRepository[Business], IBusinessRepository):
    """
    Repositorio especializado para la gestión de negocios (tenants).
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Business, db)

    async def get_by_slug(self, slug: str) -> Business | None:
        """
        Busca un negocio por su slug único. 
        Útil para cargar la tienda desde la URL del navegador.
        """
        statement = select(Business).where(Business.slug == slug)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: uuid.UUID) -> Sequence[Business]:
        """
        Obtiene la lista de todos los negocios que pertenecen a un usuario (dueño).
        """
        statement = select(Business).where(Business.owner_id == owner_id)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def check_slug_availability(self, slug: str) -> bool:
        """
        Verifica si un slug ya está registrado en el sistema.
        """
        business = await self.get_by_slug(slug)
        return business is None