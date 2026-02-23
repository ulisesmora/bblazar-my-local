import uuid
from datetime import time
from typing import Any

from pydantic import BaseModel, ConfigDict


class BusinessBase(BaseModel):
    """
    Atributos base compartidos para los negocios.
    """
    name: str
    slug: str
    image_url: str | None = None
    primary_color: str = "#4A90E2"
    secondary_color: str = "#F5A623"

class BusinessCreate(BusinessBase):
    """
    Esquema para el registro de un nuevo negocio (tenant).
    Requiere obligatoriamente el ID del dueño (owner_id).
    """
    owner_id: uuid.UUID

class BusinessUpdate(BaseModel):
    """
    Esquema para actualizar la configuración o apariencia del negocio.
    Todos los campos son opcionales.
    """
    name: str | None = None
    image_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    ai_enabled: bool | None = None
    ai_assistant_name: str | None = None
    ai_system_prompt: str | None = None
    settings: dict[str, Any] | None = None

class BusinessRead(BusinessBase):
    """
    Esquema de respuesta pública para el negocio.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    ai_enabled: bool
    ai_assistant_name: str
    
    model_config = ConfigDict(from_attributes=True)
    
    

class BusinessHourBase(BaseModel):
    day_of_week: int  # 0=Lunes, 1=Martes, etc. (o como lo decidas en tu frontend)
    open_time: time
    close_time: time
    slot_capacity: int = 5

class BusinessHourCreate(BusinessHourBase):
    business_id: uuid.UUID

class BusinessHourUpdate(BaseModel):
    day_of_week: int | None = None
    open_time: time | None = None
    close_time: time | None = None
    slot_capacity: int | None = None

class BusinessHourRead(BusinessHourBase):
    id: uuid.UUID
    business_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)