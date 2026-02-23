import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.command.Business import BusinessCommands
from app.application.query.Business import BusinessQueries
from app.domain.schemas.business import (
    BusinessCreate,
    BusinessHourCreate,
    BusinessHourRead,
    BusinessHourUpdate,
    BusinessRead,
    BusinessUpdate,
)

# Importación corregida a get_session
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# QUERIES (Lecturas - GET)
# ==========================================

@router.get("/", response_model=list[BusinessRead], status_code=status.HTTP_200_OK)
async def list_all_businesses(db: AsyncSession = Depends(get_session)): # Corregido aquí
    """Lista todos los negocios registrados en la plataforma."""
    queries = BusinessQueries(db)
    return await queries.list_all_businesses()

@router.get("/owner/{owner_id}", response_model=list[BusinessRead], status_code=status.HTTP_200_OK)
async def get_businesses_by_owner(owner_id: uuid.UUID, db: AsyncSession = Depends(get_session)): # Corregido aquí
    """Obtiene todos los negocios que pertenecen a un administrador específico."""
    queries = BusinessQueries(db)
    return await queries.get_owner_businesses(owner_id)

@router.get("/store/{slug}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
async def get_business_by_slug(slug: str, db: AsyncSession = Depends(get_session)): # Corregido aquí
    """Busca un negocio por su slug único (Ideal para cargar la tienda en el frontend)."""
    queries = BusinessQueries(db)
    return await queries.get_business_by_slug(slug)

@router.get("/{business_id}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
async def get_business_by_id(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)): # Corregido aquí
    """Obtiene los detalles de un negocio por su ID interno."""
    queries = BusinessQueries(db)
    return await queries.get_business(business_id)


# ==========================================
# COMMANDS (Escrituras - POST, PATCH, DELETE)
# ==========================================

@router.post("/", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_in: BusinessCreate, 
    db: AsyncSession = Depends(get_session) # Corregido aquí
):
    """Registra un nuevo negocio validando que el slug esté disponible."""
    commands = BusinessCommands(db)
    return await commands.create_business(business_in)

@router.patch("/{business_id}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
async def update_business(
    business_id: uuid.UUID, 
    business_in: BusinessUpdate, 
    db: AsyncSession = Depends(get_session) # Corregido aquí
):
    """Actualiza la configuración o apariencia de un negocio."""
    commands = BusinessCommands(db)
    return await commands.update_business(business_id, business_in)

@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)): # Corregido aquí
    """
    Elimina un negocio. 
    Devuelve un 204 No Content si fue exitoso (Best practice en REST).
    """
    commands = BusinessCommands(db)
    await commands.delete_business(business_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{business_id}/hours", response_model=list[BusinessHourRead], status_code=status.HTTP_200_OK)
async def get_business_hours(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene todos los horarios configurados para un negocio, ordenados por día."""
    queries = BusinessQueries(db)
    return await queries.get_business_hours(business_id)

@router.post("/hours", response_model=BusinessHourRead, status_code=status.HTTP_201_CREATED)
async def add_business_hour(hour_in: BusinessHourCreate, db: AsyncSession = Depends(get_session)):
    """Añade un nuevo bloque de horario de atención al negocio."""
    commands = BusinessCommands(db)
    return await commands.add_hour(hour_in)

@router.patch("/hours/{hour_id}", response_model=BusinessHourRead, status_code=status.HTTP_200_OK)
async def update_business_hour(
    hour_id: uuid.UUID, 
    hour_in: BusinessHourUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """Actualiza un horario existente (ej. cambiar la hora de cierre o capacidad)."""
    commands = BusinessCommands(db)
    return await commands.update_hour(hour_id, hour_in)

@router.delete("/hours/{hour_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_hour(hour_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina un bloque de horario."""
    commands = BusinessCommands(db)
    await commands.delete_hour(hour_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)