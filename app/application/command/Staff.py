import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.StaffService import StaffService
from app.domain.models.models import Staff
from app.domain.schemas.staff import StaffCreate, StaffUpdate


class StaffCommands:
    """
    Caso de Uso (SRP) para la escritura de datos del Personal (Staff).
    """
    def __init__(self, db: AsyncSession):
        self.service = StaffService(db)

    async def create_staff(self, data: StaffCreate) -> Staff:
        """Command: Registra un nuevo miembro del personal."""
        # Mapeamos los datos del esquema al modelo de base de datos.
        # Si tienes lógica especial (ej. validar que el business_id exista), 
        # tu StaffService debería encargarse de ello.
        new_staff = Staff(**data.model_dump())
        return await self.service.create(new_staff)

    async def update_staff(self, staff_id: uuid.UUID, update_data: StaffUpdate) -> Staff:
        """Command: Actualiza el perfil, bio o redes sociales de un empleado."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        try:
            return await self.service.update(staff_id, update_dict)
        except ValueError:
            # Capturamos el error genérico del BaseService y lo hacemos HTTP
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Miembro del personal no encontrado."
            )

    async def delete_staff(self, staff_id: uuid.UUID) -> bool:
        """Command: Da de baja o elimina a un miembro del personal."""
        try:
            return await self.service.delete(staff_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Miembro del personal no encontrado."
            )