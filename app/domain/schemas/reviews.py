import uuid

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# 1. ORDER REVIEW (Experiencia General)
# ==========================================
class OrderReviewCreate(BaseModel):
    business_id: uuid.UUID
    user_id: uuid.UUID
    order_id: uuid.UUID
    rating_attention: int = Field(..., ge=1, le=5)
    rating_speed: int = Field(..., ge=1, le=5)
    rating_location: int = Field(..., ge=1, le=5)
    rating_general: int = Field(..., ge=1, le=5)
    comment: str | None = None

class OrderReviewRead(OrderReviewCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 2. ITEM REVIEW (Calidad del Producto)
# ==========================================
class ItemReviewCreate(BaseModel):
    item_id: uuid.UUID
    user_id: uuid.UUID
    order_id: uuid.UUID
    rating_quality: int = Field(..., ge=1, le=5)
    comment: str | None = None

class ItemReviewRead(ItemReviewCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 3. STAFF REVIEW (Trato del Personal)
# ==========================================
class StaffReviewCreate(BaseModel):
    staff_id: uuid.UUID
    user_id: uuid.UUID
    order_id: uuid.UUID
    rating_service: int = Field(..., ge=1, le=5)
    comment: str | None = None

class StaffReviewRead(StaffReviewCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)