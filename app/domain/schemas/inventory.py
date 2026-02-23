import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    date: date
    quantity_produced: int
    quantity_available: int

class InventoryCreate(InventoryBase):
    """Esquema para registrar el stock inicial de un ítem en un día específico."""
    item_id: uuid.UUID

class InventoryUpdate(BaseModel):
    """
    Esquema para ajustar el stock manualmente. 
    (Ej. se arruinó un producto o se produjo más a mitad del día).
    """
    quantity_produced: int | None = None
    quantity_available: int | None = None

class InventoryRead(InventoryBase):
    """Esquema de salida para leer el inventario."""
    id: uuid.UUID
    item_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)