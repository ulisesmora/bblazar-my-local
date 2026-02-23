import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.CatalogService import CatalogService
from app.domain.models.models import Category, Item

# Ajusta los imports a como tengas tus schemas de catalog/category/item
from app.domain.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    ItemCreate,
    ItemUpdate,
)

# Si tienes un schema para Item, impórtalo aquí (ej. ItemCreate, ItemUpdate)

class CatalogCommands:
    """
    Caso de Uso (SRP) para la escritura de datos del Catálogo (Categorías e Ítems).
    """
    def __init__(self, db: AsyncSession):
        self.service = CatalogService(db)

    # --- CATEGORÍAS ---

    async def create_category(self, data: CategoryCreate) -> Category:
        return await self.service.create_category(data)

    async def update_category(self, category_id: uuid.UUID, update_data: CategoryUpdate) -> Category:
        update_dict = update_data.model_dump(exclude_unset=True)
        try:
            return await self.service.update_category(category_id, update_dict)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Categoría no encontrada."
            )

    async def delete_category(self, category_id: uuid.UUID) -> bool:
        """Command: Elimina una categoría."""
        try:
            return await self.service.delete(category_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Categoría no encontrada."
            )

    # --- ÍTEMS (PRODUCTOS / SERVICIOS) ---
    
    # Nota: Descomenta y ajusta estos métodos cuando tengas los schemas de Item listos
    
    async def create_item(self, data: ItemCreate) -> Item:
        return await self.service.create_item(data)

    async def update_item(self, item_id: uuid.UUID, update_data: ItemUpdate) -> Item:
        update_dict = update_data.model_dump(exclude_unset=True)
        try:
            return await self.service.update_item(item_id, update_dict)
        except ValueError:
            raise HTTPException(status_code=404, detail="Ítem no encontrado.")

    async def delete_item(self, item_id: uuid.UUID) -> bool:
        try:
            return await self.service.delete_item(item_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Ítem no encontrado.")
    