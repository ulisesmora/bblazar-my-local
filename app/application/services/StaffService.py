import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.application.services.BaseService import BaseService
from app.domain.models.models import Staff
from app.domain.services.service import IStaffService
from app.infrastructure.repositories.base import BaseRepository


class StaffService(BaseService[Staff], IStaffService):
    """
    Implementación del servicio de Personal (Staff).
    Gestiona los miembros del equipo de un negocio y sus especialidades.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.staff_repo = BaseRepository(Staff, db)
        # Inicializamos BaseService para habilitar CRUD genérico (get_by_id, update, delete)
        super().__init__(self.staff_repo)

    async def add_staff_member(
        self, 
        business_id: uuid.UUID, 
        name: str, 
        specialty: str | None = None
    ) -> Staff:
        """
        Registra un nuevo miembro en el equipo de un negocio.
        """
        new_member = Staff(
            business_id=business_id,
            name=name,
            specialty=specialty,
            is_active=True
        )
        return await self.create(new_member)

    async def get_business_staff(self, business_id: uuid.UUID) -> Sequence[Staff]:
        """
        Obtiene la lista de empleados activos de un negocio.
        Utilizado para asignar tareas en los pedidos o mostrar en el catálogo.
        """
        statement = select(Staff).where(
            Staff.business_id == business_id,
            Staff.is_active == True,
            Staff.deleted_at == None
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def toggle_staff_status(self, staff_id: uuid.UUID) -> Staff:
        """
        Activa o desactiva a un miembro del personal (ej. por vacaciones o baja).
        """
        member = await self.get_by_id(staff_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Miembro del personal no encontrado"
            )
        
        return await self.update(staff_id, {"is_active": not member.is_active})