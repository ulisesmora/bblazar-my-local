import uuid
from collections.abc import Sequence
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.application.services.InventoryService import InventoryService
from app.application.services.WalletService import WalletService
from app.domain.models.models import DailyInventory, Item, Order, OrderItem, OrderStatus
from app.domain.schemas.orders import OrderCreate
from app.domain.services.service import IOrderService
from app.infrastructure.repositories.base import BaseRepository


class OrderService(BaseService[Order], IOrderService):
    """
    Orquestador de pedidos.
    Coordina la validación de inventario, el cobro en el monedero y la creación
    de la orden de forma atómica.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = BaseRepository(Order, db)
        self.wallet_service = WalletService(db)
        self.inventory_service = InventoryService(db)
        super().__init__(self.order_repo)

    async def create_order(self, user_id: uuid.UUID, data: OrderCreate) -> Order:
        """
        Crea una orden realizando validaciones cruzadas.
        Generamos el order_id manualmente para satisfacer el constructor de OrderItem.
        """
        # Generamos el ID de la orden por adelantado para los items
        order_id = uuid.uuid4()
        total_amount = Decimal("0.0")
        order_items_list = []
        target_date = data.pickup_slot.date()

        # 1. Validar productos y disponibilidad de stock
        for entry in data.items:
            item = await self.db.get(Item, entry.item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"El producto con ID {entry.item_id} no existe."
                )
            
            # Verificar disponibilidad usando el servicio de inventario
            has_stock = await self.inventory_service.check_availability(
                item.id, target_date, entry.quantity
            )
            if not has_stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{item.name}' el día {target_date}."
                )
            
            # Calcular subtotales
            total_amount += item.price * entry.quantity
            
            # Creamos el OrderItem incluyendo el order_id para evitar errores de Pylance
            order_items_list.append(
                OrderItem(
                    order_id=order_id,
                    item_id=item.id,
                    quantity=entry.quantity,
                    unit_price=item.price,
                    staff_id=entry.staff_id
                )
            )

        # 2. Procesar el pago (Débito en Wallet)
        await self.wallet_service.add_funds(
            user_id=user_id,
            business_id=data.business_id,
            amount=-total_amount,
            description=f"Compra en local - Slot: {data.pickup_slot}"
        )

        # 3. Descontar Stock e instanciar la Orden
        for entry in data.items:
            stmt = select(DailyInventory).where(
                DailyInventory.item_id == entry.item_id,
                DailyInventory.date == target_date
            )
            res = await self.db.execute(stmt)
            inv_record = res.scalar_one()
            inv_record.quantity_available -= entry.quantity
            self.db.add(inv_record)

        # 4. Crear la Orden con el ID pre-generado y los items vinculados
        new_order = Order(
            id=order_id,
            business_id=data.business_id,
            user_id=user_id,
            status=OrderStatus.PAID,
            total_amount=total_amount,
            pickup_slot=data.pickup_slot,
            items=order_items_list
        )
        
        # 5. Guardar y confirmar transacción atómica
        created_order = await self.order_repo.create(new_order)
        await self.db.commit()
        await self.db.refresh(created_order)
        
        return created_order

    async def get_user_orders(self, user_id: uuid.UUID) -> Sequence[Order]:
        """
        Obtiene el historial de órdenes del usuario.
        Se usa col().desc() para evitar errores de tipo con datetime en Pylance.
        """
        statement = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(col(Order.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()