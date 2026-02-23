import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.command.KnoledgeSource import KnowledgeCommands
from app.application.query.KnoledgeSource import KnowledgeQueries
from app.domain.schemas.knowledge import (
    KnowledgeSourceCreate,
    KnowledgeSourceRead,
    KnowledgeSourceUpdate,
)
from app.infrastructure.database.database import get_session

router = APIRouter()

# --- LECTURAS (QUERIES) ---
@router.get("/business/{business_id}", response_model=list[KnowledgeSourceRead])
async def list_business_knowledge(
    business_id: uuid.UUID, 
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_session)
):
    """Obtiene todos los documentos y enlaces con los que se entrena al bot de un negocio."""
    queries = KnowledgeQueries(db)
    return await queries.get_business_knowledge(business_id, active_only)

@router.get("/{source_id}", response_model=KnowledgeSourceRead)
async def get_knowledge_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    queries = KnowledgeQueries(db)
    return await queries.get_source(source_id)

# --- ESCRITURAS (COMMANDS) ---
@router.post("/", response_model=KnowledgeSourceRead, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_source(data_in: KnowledgeSourceCreate, db: AsyncSession = Depends(get_session)):
    """Sube un nuevo documento, texto plano o URL para el bot MCP."""
    commands = KnowledgeCommands(db)
    return await commands.add_source(data_in)

@router.patch("/{source_id}", response_model=KnowledgeSourceRead)
async def update_knowledge_source(
    source_id: uuid.UUID, 
    data_in: KnowledgeSourceUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """Modifica el texto, cambia la URL o desactiva un documento."""
    commands = KnowledgeCommands(db)
    return await commands.update_source(source_id, data_in)

@router.patch("/{source_id}/indexed", response_model=KnowledgeSourceRead)
async def mark_source_as_indexed(source_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Marca que el worker de IA ya procesó/vectorizó esta fuente de conocimiento."""
    commands = KnowledgeCommands(db)
    return await commands.set_indexed(source_id)

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina (soft-delete) un documento del sistema."""
    commands = KnowledgeCommands(db)
    await commands.delete_source(source_id)