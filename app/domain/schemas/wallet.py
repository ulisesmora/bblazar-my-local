import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import TransactionType


class WalletRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    balance: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class WalletTransactionRead(BaseModel):
    id: uuid.UUID
    wallet_id: uuid.UUID
    amount: Decimal
    type: TransactionType
    description: str
    created_at: datetime
    reference_id: uuid.UUID | None = None
    
    model_config = ConfigDict(from_attributes=True)

class RechargePlanRead(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    price: Decimal
    credit: Decimal
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)