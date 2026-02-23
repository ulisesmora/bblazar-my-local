import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import OrderStatus

# ==========================================
# DETALLE DEL PEDIDO (OrderItem)
# ==========================================

class OrderItemBase(BaseModel):
    item_id: uuid.UUID
    quantity: int
    staff_id: uuid.UUID | None = None # Por si el usuario eligió a un barbero/entrenador específico

class OrderItemRead(OrderItemBase):
    id: uuid.UUID
    order_id: uuid.UUID
    unit_price: Decimal
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# CABECERA DEL PEDIDO (Order)
# ==========================================

class OrderCreate(BaseModel):
    """
    Esquema que envía el Frontend (El Carrito de Compras).
    Nota: El total no se envía, se calcula en el backend por seguridad.
    """
    business_id: uuid.UUID
    user_id: uuid.UUID
    pickup_slot: datetime
    items: list[OrderItemBase]

class OrderStatusUpdate(BaseModel):
    """Esquema para que el negocio cambie el estado del pedido (Ej. de PENDING a PREPARING)."""
    status: OrderStatus

class OrderRead(BaseModel):
    """Esquema de salida con la información principal del pedido."""
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: uuid.UUID
    status: OrderStatus
    total_amount: Decimal
    pickup_slot: datetime
    is_subscription_order: bool
    
    # Podemos incluir los items directamente en la respuesta si es útil para el frontend
    items: list[OrderItemRead] = []
    
    model_config = ConfigDict(from_attributes=True)