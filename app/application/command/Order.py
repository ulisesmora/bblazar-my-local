import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.CatalogService import CatalogService
from app.application.services.InventoryService import InventoryService
from app.application.services.OrdersService import OrdersService
from app.application.services.WalletService import WalletService
from app.domain.models.models import Order, OrderItem, OrderStatus
from app.domain.schemas.orders import OrderCreate, OrderStatusUpdate


class OrderCommands:
    """
    Caso de Uso que orquesta la creación del pedido interactuando con Catálogo, 
    Inventario, Billetera y Pedidos.
    """
    def __init__(self, db: AsyncSession):
        self.orders_service = OrdersService(db)
        self.catalog_service = CatalogService(db)
        self.inventory_service = InventoryService(db)
        self.wallet_service = WalletService(db)

    
    async def create_order(self, data: OrderCreate) -> Order:
        # ¡Generamos el ID de la orden por adelantado! 
        # (Exactamente como lo tenías en tu código original)
        order_id = uuid.uuid4() 
        
        total_amount = Decimal("0.0")
        order_items_list = []
        target_date = data.pickup_slot.date()

        # 1. Validar Catálogo e Inventario
        for entry in data.items:
            # Validar que exista y obtener precio real
            item_db = await self.catalog_service.get_item_by_id(entry.item_id)
            if not item_db:
                raise HTTPException(status_code=404, detail=f"El producto con ID {entry.item_id} no existe.")
            
            # Validar disponibilidad
            has_stock = await self.inventory_service.check_availability(item_db.id, target_date, entry.quantity)
            if not has_stock:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para '{item_db.name}' el día {target_date}.")
            
            total_amount += item_db.price * entry.quantity
            
            order_items_list.append(
                OrderItem(
                    order_id=order_id, # <-- AQUÍ usamos el ID pre-generado
                    item_id=item_db.id,
                    quantity=entry.quantity,
                    unit_price=item_db.price,
                    staff_id=entry.staff_id
                )
            )

        # 2. Cobrar del Monedero
        try:
            await self.wallet_service.deduct_funds(
                user_id=data.user_id,
                business_id=data.business_id,
                amount=total_amount,
                description=f"Compra de pedido para {target_date}"
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) # "Saldo insuficiente"

        # 3. Descontar Inventario
        for entry in data.items:
            inv_record = await self.inventory_service.get_by_item_and_date(entry.item_id, target_date)
            if inv_record:
                new_qty = inv_record.quantity_available - entry.quantity
                await self.inventory_service.update(inv_record.id, {"quantity_available": new_qty})

        # 4. Construir y guardar la Orden
        new_order = Order(
            id=order_id, # <-- AQUÍ le asignamos el mismo ID a la cabecera
            business_id=data.business_id,
            user_id=data.user_id,
            pickup_slot=data.pickup_slot,
            total_amount=total_amount,
            status=OrderStatus.PAID
        )
        

        return await self.orders_service.save_full_order(new_order, order_items_list)
    async def update_status(self, order_id: uuid.UUID, data: OrderStatusUpdate) -> Order:
        try:
            return await self.orders_service.update_order_status(order_id, data.status)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))