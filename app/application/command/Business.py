import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.BusinessService import (
    BusinessService,  # <-- USAMOS TU SERVICIO
)
from app.domain.models.models import Business
from app.domain.schemas.business import (
    BusinessCreate,
    BusinessHourCreate,
    BusinessHourUpdate,
    BusinessUpdate,
)
from app.infrastructure.repositories.business_repo import BusinessRepository


class BusinessCommands:
    """
    Caso de Uso (SRP) para la escritura de Negocios.
    Delega la lógica pesada al BusinessService.
    """
    def __init__(self, db: AsyncSession):
        # Instanciamos el servicio (que por dentro usará su repositorio)
        BusinessRepository(db)
        self.service = BusinessService(db)

    async def create_business(self, data: BusinessCreate) -> Business:
        """Command: Registra un negocio nuevo."""
        
        # 1. Podemos usar el servicio para la validación específica
        # (Asumiendo que agregaste este método a tu BusinessService)
        is_available = await self.service.check_slug_availability(data.slug)
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El identificador (slug) del negocio ya está en uso."
            )
            
        new_business = Business(
            owner_id=data.owner_id,
            name=data.name,
            slug=data.slug,
            image_url=data.image_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color
        )
        
        # 2. Reutilizamos el create() de tu BaseService heredado
        return await self.service.create(new_business)

    async def update_business(self, business_id: uuid.UUID, update_data: BusinessUpdate) -> Business:
        """Command: Actualiza datos de un negocio."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        try:
            # Tu BaseService ya hace el get_by_id y levanta ValueError si no existe
            return await self.service.update(business_id, update_dict)
        except ValueError as e:
            # El Command traduce el error de negocio (ValueError) a un error HTTP
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e)
            )

    async def delete_business(self, business_id: uuid.UUID) -> bool:
        """Command: Elimina un negocio."""
        try:
            # Reutilizamos el delete() de tu BaseService
            return await self.service.delete(business_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e)
            )
            
    
    async def add_hour(self, data: BusinessHourCreate):
        return await self.service.add_business_hour(data.model_dump())

    async def update_hour(self, hour_id: uuid.UUID, data: BusinessHourUpdate):
        try:
            return await self.service.update_business_hour(hour_id, data.model_dump(exclude_unset=True))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def delete_hour(self, hour_id: uuid.UUID):
        try:
            return await self.service.delete_business_hour(hour_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))