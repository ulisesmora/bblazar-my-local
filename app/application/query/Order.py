import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.OrdersService import OrdersService
from app.domain.models.models import Order, OrderStatus


class OrderQueries:
    """
    Caso de Uso (SRP) para la lectura de pedidos.
    Solo se encarga de consultar el estado y el historial, sin modificar datos.
    """
    def __init__(self, db: AsyncSession):
        self.service = OrdersService(db)

    async def get_order_details(self, order_id: uuid.UUID) -> Order:
        """Query: Obtiene un pedido con todo su detalle de productos."""
        order = await self.service.get_order_with_items(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Pedido no encontrado."
            )
        return order

    async def get_business_orders(self, business_id: uuid.UUID, status_filter: OrderStatus | None = None) -> Sequence[Order]:
        """Query: Lista los pedidos de un negocio (Ideal para el panel de administración del local)."""
        return await self.service.get_business_orders(business_id, status_filter)

    async def get_user_orders(self, user_id: uuid.UUID) -> Sequence[Order]:
        """Query: Lista el historial de compras de un cliente (Ideal para la sección 'Mis Pedidos' del usuario)."""
        return await self.service.get_user_orders(user_id)