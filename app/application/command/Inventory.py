import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.InventoryService import InventoryService
from app.domain.models.models import DailyInventory
from app.domain.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryCommands:
    """
    Caso de Uso (SRP) para la escritura de datos de Inventario Diario.
    Maneja la creación, actualización y eliminación de stock.
    """
    def __init__(self, db: AsyncSession):
        self.service = InventoryService(db)

    async def register_daily_stock(self, data: InventoryCreate) -> DailyInventory:
        """Command: Registra estrictamente el stock inicial. Falla si ya existe."""
        return await self.service.create_inventory(data)

    async def set_stock(self, item_id: uuid.UUID, target_date: date, quantity: int) -> DailyInventory:
        """
        Command: Establece el stock de forma segura (Upsert). 
        Si no existe lo crea, si existe lo sobrescribe.
        """
        return await self.service.set_daily_stock(item_id, target_date, quantity)

    async def update_daily_stock(self, inventory_id: uuid.UUID, update_data: InventoryUpdate) -> DailyInventory:
        """Command: Ajuste parcial de un registro de inventario existente."""
        update_dict = update_data.model_dump(exclude_unset=True)
        try:
            return await self.service.update(inventory_id, update_dict)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Registro de inventario no encontrado."
            )

    async def delete_daily_stock(self, inventory_id: uuid.UUID) -> bool:
        """Command: Elimina un registro de inventario (soft delete)."""
        try:
            return await self.service.delete(inventory_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Registro de inventario no encontrado."
            )