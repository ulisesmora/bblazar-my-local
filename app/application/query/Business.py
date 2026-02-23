import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.BusinessService import BusinessService
from app.domain.models.models import Business


class BusinessQueries:
    """
    Caso de Uso (SRP) para la lectura de datos de Negocios (Tenants).
    Delega la lógica al BusinessService para mantener la consistencia.
    """
    def __init__(self, db: AsyncSession):
        # Según la definición de tu BusinessService, este recibe la sesión de DB
        self.service = BusinessService(db)

    async def get_business(self, business_id: uuid.UUID) -> Business:
        """
        Query: Obtiene los detalles de un negocio por su ID.
        """
        business = await self.service.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negocio no encontrado"
            )
        return business

    async def get_business_by_slug(self, slug: str) -> Business:
        """
        Query: Obtiene un negocio por su slug amigable.
        Útil para la carga inicial de la tienda en el frontend.
        """
        # Tu servicio ya maneja la excepción 404 para este método, 
        # así que simplemente lo llamamos y retornamos el resultado.
        return await self.service.get_business_by_slug(slug)

    async def get_owner_businesses(self, owner_id: uuid.UUID) -> Sequence[Business]:
        """
        Query: Lista todos los negocios que le pertenecen a un dueño específico.
        """
        return await self.service.get_owner_businesses(owner_id)

    async def list_all_businesses(self) -> Sequence[Business] | None:
        """
        Query: Lista todos los negocios del sistema (podría ser útil para un SuperAdmin).
        """
        return await self.service.list_all()
    
    async def get_business_hours(self, business_id: uuid.UUID):
        return await self.service.get_business_hours(business_id)