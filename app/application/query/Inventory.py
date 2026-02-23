import uuid
from collections.abc import Sequence
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.InventoryService import InventoryService
from app.domain.models.models import DailyInventory


class InventoryQueries:
    """
    Caso de Uso (SRP) para la lectura de datos de Inventario.
    Maneja consultas de historial, stock actual y disponibilidad.
    """
    def __init__(self, db: AsyncSession):
        self.service = InventoryService(db)

    async def get_inventory_record(self, inventory_id: uuid.UUID) -> DailyInventory:
        """Query: Obtiene un registro de inventario específico por su ID."""
        record = await self.service.get_by_id(inventory_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Registro de inventario no encontrado."
            )
        return record

    async def get_stock_for_date(self, item_id: uuid.UUID, target_date: date) -> DailyInventory:
        """Query: Obtiene el stock exacto de un producto en una fecha."""
        record = await self.service.get_by_item_and_date(item_id, target_date)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No hay registro de inventario para este producto en la fecha {target_date}."
            )
        return record

    async def get_item_history(self, item_id: uuid.UUID) -> Sequence[DailyInventory]:
        """Query: Lista el historial de stock de un producto."""
        return await self.service.get_history_by_item(item_id)

    async def check_item_availability(self, item_id: uuid.UUID, target_date: date, requested_qty: int) -> dict:
        """
        Query: Evalúa si un producto puede ser vendido en una fecha según la cantidad solicitada.
        Devuelve un diccionario estructurado, muy útil para validaciones previas al carrito.
        """
        is_available = await self.service.check_availability(item_id, target_date, requested_qty)
        return {
            "item_id": item_id,
            "date": target_date,
            "requested_quantity": requested_qty,
            "is_available": is_available
        }