import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import OrderStatus


class OrderItemBase(BaseModel):
    item_id: uuid.UUID
    quantity: int
    staff_id: uuid.UUID | None = None

class OrderItemRead(OrderItemBase):
    id: uuid.UUID
    unit_price: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    business_id: uuid.UUID
    items: list[OrderItemBase]
    pickup_slot: datetime

class OrderRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    status: OrderStatus
    total_amount: Decimal
    pickup_slot: datetime
    created_at: datetime
    items: list[OrderItemRead]
    
    model_config = ConfigDict(from_attributes=True)