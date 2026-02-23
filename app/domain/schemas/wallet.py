import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import TransactionType

# ==========================================
# PLANES DE RECARGA (Recharge Plan)
# ==========================================

class RechargePlanBase(BaseModel):
    price: Decimal
    credit: Decimal
    is_active: bool = True

class RechargePlanCreate(RechargePlanBase):
    business_id: uuid.UUID

class RechargePlanUpdate(BaseModel):
    price: Decimal | None = None
    credit: Decimal | None = None
    is_active: bool | None = None

class RechargePlanRead(RechargePlanBase):
    id: uuid.UUID
    business_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# MONEDERO (Wallet)
# ==========================================

class WalletRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    balance: Decimal
    
    model_config = ConfigDict(from_attributes=True)

# No hacemos un "WalletCreate" expuesto a la API de forma tradicional, 
# porque el Wallet se debería crear automáticamente la primera vez que 
# un usuario interactúa o recarga saldo en un negocio.

# ==========================================
# TRANSACCIONES (Wallet Transaction)
# ==========================================

class TransactionCreate(BaseModel):
    """Esquema interno para registrar un movimiento."""
    wallet_id: uuid.UUID
    amount: Decimal
    type: TransactionType
    description: str
    reference_id: uuid.UUID | None = None
    external_reference: str | None = None

class TransactionRead(BaseModel):
    id: uuid.UUID
    wallet_id: uuid.UUID
    amount: Decimal
    type: TransactionType
    description: str
    reference_id: uuid.UUID | None = None
    external_reference: str | None = None
    
    model_config = ConfigDict(from_attributes=True)