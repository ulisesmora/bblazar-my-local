import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos los casos de uso (Commands y Queries)
from app.application.command.Staff import StaffCommands
from app.application.query.Staff import StaffQueries

# Importamos los esquemas (DTOs)
from app.domain.schemas.staff import StaffCreate, StaffRead, StaffUpdate

# Importamos la dependencia de base de datos correcta
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# QUERIES (Lecturas - GET)
# ==========================================

@router.get("/{staff_id}", response_model=StaffRead, status_code=status.HTTP_200_OK)
async def get_staff_details(
    staff_id: uuid.UUID, 
    db: AsyncSession = Depends(get_session)
):
    """Obtiene el perfil detallado de un miembro del staff."""
    queries = StaffQueries(db)
    return await queries.get_staff(staff_id)

@router.get("/business/{business_id}", response_model=list[StaffRead], status_code=status.HTTP_200_OK)
async def get_staff_by_business(
    business_id: uuid.UUID, 
    db: AsyncSession = Depends(get_session)
):
    """
    Lista todo el personal asociado a un negocio.
    Útil para mostrar la pantalla de 'Nuestro Equipo'.
    """
    queries = StaffQueries(db)
    return await queries.get_staff_by_business(business_id)

# ==========================================
# COMMANDS (Escrituras - POST, PATCH, DELETE)
# ==========================================

@router.post("/", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
async def create_staff_member(
    staff_in: StaffCreate, 
    db: AsyncSession = Depends(get_session)
):
    """
    Registra un nuevo empleado.
    Requiere el ID del negocio en el cuerpo de la petición.
    """
    commands = StaffCommands(db)
    return await commands.create_staff(staff_in)

@router.patch("/{staff_id}", response_model=StaffRead, status_code=status.HTTP_200_OK)
async def update_staff_member(
    staff_id: uuid.UUID, 
    staff_in: StaffUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """Actualiza datos del empleado (Bio, especialidad, foto, etc.)."""
    commands = StaffCommands(db)
    return await commands.update_staff(staff_id, staff_in)

@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_member(
    staff_id: uuid.UUID, 
    db: AsyncSession = Depends(get_session)
):
    """Elimina (o desactiva) un miembro del staff."""
    commands = StaffCommands(db)
    await commands.delete_staff(staff_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)