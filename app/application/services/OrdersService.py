import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.domain.models.models import Order, OrderItem, OrderStatus
from app.domain.services.service import IOrderService
from app.infrastructure.repositories.base import BaseRepository


class OrdersService(BaseService[Order], IOrderService):
    """
    Servicio exclusivo para la gestión de datos de pedidos y sus líneas de detalle.
    La orquestación de inventario y cobros se delega a la capa de Commands.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = BaseRepository(Order, db)
        self.item_repo = BaseRepository(OrderItem, db)
        super().__init__(self.order_repo)

    async def save_full_order(self, new_order: Order, items: list[OrderItem]) -> Order:
        """
        Guarda la cabecera del pedido y sus líneas de detalle.
        """
        saved_order = await self.order_repo.create(new_order)
        
        for item in items:
            await self.item_repo.create(item)
            
        return await self.get_order_with_items(saved_order.id) # type: ignore

    async def get_order_with_items(self, order_id: uuid.UUID) -> Order | None:
        statement = select(Order).where(
            Order.id == order_id
        ).options(selectinload(Order.items)) # type: ignore
        
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def update_order_status(self, order_id: uuid.UUID, new_status: OrderStatus) -> Order:
        order = await self.order_repo.get(order_id)
        if not order:
            raise ValueError("Pedido no encontrado.")
        return await self.order_repo.update(order, {"status": new_status})

    async def get_business_orders(self, business_id: uuid.UUID, status_filter: OrderStatus | None = None) -> Sequence[Order]:
        statement = select(Order).where(
            Order.business_id == business_id
        ).options(selectinload(Order.items)) # type: ignore
        
        if status_filter:
            statement = statement.where(Order.status == status_filter)
            
        statement = statement.order_by(col(Order.created_at).desc())
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_user_orders(self, user_id: uuid.UUID) -> Sequence[Order]:
        statement = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items)) # type: ignore
            .order_by(col(Order.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()