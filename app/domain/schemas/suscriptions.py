import uuid
from datetime import datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

# ==========================================
# DETALLE DE SUSCRIPCIÓN (SubscriptionItem)
# ==========================================

class SubscriptionItemBase(BaseModel):
    item_id: uuid.UUID
    quantity: int
    unit_price: Decimal

class SubscriptionItemRead(SubscriptionItemBase):
    id: uuid.UUID
    subscription_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionPaymentRead(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID
    amount: Decimal
    status: str
    payment_date: datetime
    external_reference: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    user_id: uuid.UUID
    business_id: uuid.UUID
    frequency_days: str   
    pickup_time: time
    current_period_start: datetime
    items: list[SubscriptionItemBase]

class SubscriptionStatusUpdate(BaseModel):
    status: str
    current_period_end: datetime | None = None

class SubscriptionRead(BaseModel):
    """Esquema de salida completo."""
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    frequency_days: int
    pickup_time: time
    items: list[SubscriptionItemRead] = []
    model_config = ConfigDict(from_attributes=True)