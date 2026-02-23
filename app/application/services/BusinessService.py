import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.domain.models.models import Business, BusinessHour  # Agregamos BusinessHour
from app.domain.schemas.business import BusinessCreate
from app.domain.services.service import IBusinessService
from app.infrastructure.repositories.base import BaseRepository  # Importante
from app.infrastructure.repositories.business_repo import BusinessRepository


class BusinessService(BaseService[Business], IBusinessService):
    def __init__(self, db: AsyncSession):
        self.db = db
        # Repositorio específico de negocios
        self.business_repo = BusinessRepository(db)
        # Repositorio genérico para los horarios
        self.hour_repo = BaseRepository(BusinessHour, db)
        
        super().__init__(self.business_repo)
        
    # ==========================================
    # LÓGICA DE NEGOCIOS (BUSINESS)
    # ==========================================
    
    async def check_slug_availability(self, slug: str) -> bool:
        return await self.business_repo.check_slug_availability(slug)

    async def register_business(self, data: BusinessCreate) -> Business:
        is_available = await self.check_slug_availability(data.slug)
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El identificador '{data.slug}' ya está registrado por otro comercio."
            )

        new_business = Business(
            owner_id=data.owner_id,
            name=data.name,
            slug=data.slug.lower().strip().replace(" ", "-"),
            image_url=data.image_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color
        )
        return await self.create(new_business)

    async def get_owner_businesses(self, owner_id: uuid.UUID) -> Sequence[Business]:
        return await self.business_repo.get_by_owner(owner_id)

    async def get_business_by_slug(self, slug: str) -> Business:
        business = await self.business_repo.get_by_slug(slug)
        if not business:
            raise HTTPException(status_code=404, detail="Negocio no encontrado")
        return business

    async def update_mcp_config(self, business_id: uuid.UUID, prompt: str, bot_name: str) -> Business:
        business = await self.get_by_id(business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Negocio no encontrado")
            
        update_data = {
            "ai_system_prompt": prompt,
            "ai_assistant_name": bot_name,
            "ai_enabled": True
        }
        return await self.update(business_id, update_data)

    # ==========================================
    # LÓGICA DE HORARIOS (BUSINESS HOUR)
    # ==========================================

    async def add_business_hour(self, data: dict) -> BusinessHour:
        """Añade un nuevo bloque de horario de atención al negocio."""
        new_hour = BusinessHour(**data)
        return await self.hour_repo.create(new_hour)

    async def get_business_hours(self, business_id: uuid.UUID) -> Sequence[BusinessHour]:
        """Obtiene todos los horarios configurados para un negocio, ordenados por día."""
        
        # 2. Envuelve el campo con col() en el order_by
        statement = select(BusinessHour).where(
            BusinessHour.business_id == business_id,
            BusinessHour.deleted_at == None
        ).order_by(col(BusinessHour.day_of_week)) # <--- El cambio mágico aquí
        
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def update_business_hour(self, hour_id: uuid.UUID, update_data: dict) -> BusinessHour:
        """Actualiza un horario existente."""
        hour = await self.hour_repo.get(hour_id)
        if not hour:
            raise ValueError("Horario no encontrado")
        return await self.hour_repo.update(hour, update_data)

    async def delete_business_hour(self, hour_id: uuid.UUID) -> bool:
        """Elimina un bloque de horario."""
        hour = await self.hour_repo.get(hour_id)
        if not hour:
            raise ValueError("Horario no encontrado")
        return await self.hour_repo.delete(hour_id)