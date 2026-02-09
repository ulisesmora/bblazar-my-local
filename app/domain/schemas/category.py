import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import ItemType

# --- CATEGORÍAS ---

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    business_id: uuid.UUID

class CategoryRead(CategoryBase):
    id: uuid.UUID
    business_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# --- ITEMS (PRODUCTOS/SERVICIOS) ---

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    type: ItemType = ItemType.PRODUCT
    image_url: str | None = None
    is_subscription_eligible: bool = False

class ItemCreate(ItemBase):
    business_id: uuid.UUID
    category_id: uuid.UUID

class ItemRead(ItemBase):
    id: uuid.UUID
    business_id: uuid.UUID
    category_id: uuid.UUID
    stripe_price_id: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

# --- INVENTARIO ---

class DailyInventoryBase(BaseModel):
    quantity_produced: int

class DailyInventoryRead(DailyInventoryBase):
    id: uuid.UUID
    item_id: uuid.UUID
    date: str
    quantity_available: int
    
    model_config = ConfigDict(from_attributes=True)