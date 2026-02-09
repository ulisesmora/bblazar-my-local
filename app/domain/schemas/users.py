import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.models.models import UserRole


class UserBase(BaseModel):
    phone: str
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole = UserRole.GUEST

class UserCreate(UserBase):
    """Esquema para el registro de nuevos usuarios"""
    password: str

class UserUpdate(BaseModel):
    """Esquema para actualizar datos de usuario"""
    email: EmailStr | None = None
    full_name: str | None = None
    image_url: str | None = None

class UserRead(UserBase):
    """Esquema de respuesta (sin datos sensibles como password)"""
    id: uuid.UUID
    trust_score: int
    image_url: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)