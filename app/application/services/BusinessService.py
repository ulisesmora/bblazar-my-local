import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.BaseService import BaseService
from app.domain.models.models import Business
from app.domain.schemas.business import BusinessCreate
from app.domain.services.service import IBusinessService
from app.infrastructure.repositories.business_repo import BusinessRepository


class BusinessService(BaseService[Business], IBusinessService):
    """
    Implementación del servicio de Negocios (Tenants).
    Gestiona la configuración del local y la personalización del bot MCP.
    """
    def __init__(self, db: AsyncSession):
        # Inicializamos el repositorio específico de negocios
        self.business_repo = BusinessRepository(db)
        # Pasamos el repositorio al constructor de BaseService para habilitar CRUD genérico
        super().__init__(self.business_repo)

    async def register_business(self, data: BusinessCreate) -> Business:
        """
        Registra un nuevo negocio validando que el identificador (slug) sea único.
        Transforma el nombre en un formato amigable para URL si es necesario.
        """
        # 1. Validar disponibilidad del slug
        is_available = await self.business_repo.check_slug_availability(data.slug)
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El identificador '{data.slug}' ya está registrado por otro comercio."
            )

        # 2. Preparar el nuevo objeto de negocio
        new_business = Business(
            owner_id=data.owner_id,
            name=data.name,
            slug=data.slug.lower().strip().replace(" ", "-"),
            image_url=data.image_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color
        )
        
        # 3. Guardar usando la lógica de creación del BaseService
        return await self.create(new_business)

    async def get_owner_businesses(self, owner_id: uuid.UUID) -> Sequence[Business]:
        """
        Obtiene todos los negocios que pertenecen a un administrador específico.
        """
        return await self.business_repo.get_by_owner(owner_id)

    async def get_business_by_slug(self, slug: str) -> Business:
        """
        Localiza un negocio por su slug. Crítico para la carga dinámica del frontend
        y para el contexto de las herramientas del protocolo MCP.
        """
        business = await self.business_repo.get_by_slug(slug)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negocio no encontrado"
            )
        return business

    async def update_mcp_config(
        self, business_id: uuid.UUID, prompt: str, bot_name: str
    ) -> Business:
        """
        Configura la personalidad y el conocimiento de la IA para este negocio.
        Actualiza el system prompt y el nombre que usará el asistente virtual.
        """
        # Verificamos que el negocio exista primero
        business = await self.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Negocio no encontrado"
            )
            
        # Actualizamos solo los campos de configuración de IA
        update_data = {
            "ai_system_prompt": prompt,
            "ai_assistant_name": bot_name,
            "ai_enabled": True
        }
        
        return await self.update(business_id, update_data)