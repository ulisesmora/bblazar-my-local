import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.CatalogService import CatalogService
from app.domain.models.models import Category, Item


class CatalogQueries:
    """
    Caso de Uso (SRP) para la lectura de datos del Catálogo (Categorías e Ítems).
    Delega las consultas al CatalogService y maneja las respuestas HTTP.
    """
    def __init__(self, db: AsyncSession):
        self.service = CatalogService(db)

    # ==========================================
    # QUERIES DE CATEGORÍAS
    # ==========================================

    async def get_category(self, category_id: uuid.UUID) -> Category:
        """Query: Obtiene el detalle de una categoría por su ID."""
        category = await self.service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Categoría no encontrada."
            )
        return category

    async def get_categories_by_business(self, business_id: uuid.UUID) -> Sequence[Category]:
        """Query: Lista todas las categorías (el menú) de un negocio."""
        return await self.service.get_categories_by_business(business_id)

    # ==========================================
    # QUERIES DE ÍTEMS (PRODUCTOS / SERVICIOS)
    # ==========================================

    async def get_item(self, item_id: uuid.UUID) -> Item:
        """Query: Obtiene el detalle de un producto o servicio específico."""
        item = await self.service.get_item_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Producto o servicio no encontrado."
            )
        return item

    async def get_items_by_business(self, business_id: uuid.UUID) -> Sequence[Item]:
        """Query: Lista todo el catálogo de productos/servicios de un negocio."""
        return await self.service.get_items_by_business(business_id)

    async def get_items_by_category(self, category_id: uuid.UUID) -> Sequence[Item]:
        """Query: Lista los productos/servicios que pertenecen a una categoría específica."""
        # Opcional: Podrías validar primero si la categoría existe, 
        # pero devolver una lista vacía también es completamente válido en REST.
        return await self.service.get_items_by_category(category_id)