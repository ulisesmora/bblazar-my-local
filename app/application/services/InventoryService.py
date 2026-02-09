import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.application.services.BaseService import BaseService
from app.domain.models.models import DailyInventory
from app.domain.services.service import IInventoryService
from app.infrastructure.repositories.base import BaseRepository


class InventoryService(BaseService[DailyInventory], IInventoryService):
    """
    Implementación del servicio de Inventario.
    Gestiona la disponibilidad de productos por día, permitiendo un control
    estricto sobre lo que se puede vender en cada jornada.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_repo = BaseRepository(DailyInventory, db)
        # Inicializamos BaseService para permitir operaciones CRUD sobre el historial de inventario
        super().__init__(self.inventory_repo)

    async def set_daily_stock(self, item_id: uuid.UUID, target_date: date, quantity: int) -> DailyInventory:
        """
        Establece la cantidad producida y disponible para un ítem en una fecha dada.
        Si ya existe un registro, actualiza las cantidades.
        """
        statement = select(DailyInventory).where(
            DailyInventory.item_id == item_id,
            DailyInventory.date == target_date
        )
        result = await self.db.execute(statement)
        inventory = result.scalar_one_or_none()

        if inventory:
            return await self.inventory_repo.update(
                inventory, 
                {"quantity_produced": quantity, "quantity_available": quantity}
            )
        
        new_inv = DailyInventory(
            item_id=item_id,
            date=target_date,
            quantity_produced=quantity,
            quantity_available=quantity
        )
        return await self.inventory_repo.create(new_inv)

    async def check_availability(self, item_id: uuid.UUID, target_date: date, requested_qty: int) -> bool:
        """
        Verifica si hay suficiente existencia disponible para cubrir una solicitud.
        """
        statement = select(DailyInventory).where(
            DailyInventory.item_id == item_id,
            DailyInventory.date == target_date
        )
        result = await self.db.execute(statement)
        inventory = result.scalar_one_or_none()
        
        if not inventory:
            return False
            
        return inventory.quantity_available >= requested_qty