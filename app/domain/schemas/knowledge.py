import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models.models import KnowledgeSourceType


class KnowledgeSourceBase(BaseModel):
    title: str = Field(..., description="Título del documento (Ej. 'Menú', 'Políticas')")
    content: str | None = Field(None, description="Texto plano si es de tipo TEXT")
    source_url: str | None = Field(None, description="URL web o link del archivo si es FILE/WEBSITE")
    source_type: KnowledgeSourceType = Field(default=KnowledgeSourceType.TEXT)
    is_active: bool = True

class KnowledgeSourceCreate(KnowledgeSourceBase):
    business_id: uuid.UUID

class KnowledgeSourceUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    source_url: str | None = None
    source_type: KnowledgeSourceType | None = None
    is_active: bool | None = None

class KnowledgeSourceRead(KnowledgeSourceBase):
    id: uuid.UUID
    business_id: uuid.UUID
    last_indexed_at: datetime | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)