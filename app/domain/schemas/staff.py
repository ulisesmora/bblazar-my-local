import uuid

from pydantic import BaseModel, ConfigDict

from app.domain.models.models import KnowledgeSourceType

# --- STAFF ---

class StaffBase(BaseModel):
    name: str
    specialty: str | None = None
    bio: str | None = None
    image_url: str | None = None
    social_links: dict[str, str] | None = None

class StaffRead(StaffBase):
    id: uuid.UUID
    business_id: uuid.UUID
    rating_avg: float
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# --- MCP KNOWLEDGE BASE ---


class StaffCreate(StaffBase):
    """
    Esquema para registrar un nuevo empleado.
    Requiere obligatoriamente el ID del negocio al que pertenece.
    """
    business_id: uuid.UUID
    user_id: uuid.UUID | None = None # Opcional: por si el staff también tiene cuenta de usuario en la app

class StaffUpdate(BaseModel):
    """
    Esquema para actualizar un empleado. 
    Todos los campos son opcionales para permitir actualizaciones parciales (PATCH).
    """
    name: str | None = None
    specialty: str | None = None
    bio: str | None = None
    image_url: str | None = None
    social_links: dict[str, str] | None = None
    is_active: bool | None = None # Útil para "borrado lógico" o suspender a un empleado

class KnowledgeSourceBase(BaseModel):
    title: str
    content: str | None = None
    source_url: str | None = None
    source_type: KnowledgeSourceType = KnowledgeSourceType.TEXT

class KnowledgeSourceCreate(KnowledgeSourceBase):
    business_id: uuid.UUID

class KnowledgeSourceRead(KnowledgeSourceBase):
    id: uuid.UUID
    business_id: uuid.UUID
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)