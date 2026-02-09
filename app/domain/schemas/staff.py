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