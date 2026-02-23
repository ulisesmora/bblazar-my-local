import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.StaffService import StaffService
from app.domain.models.models import Staff


class StaffQueries:
    """
    Caso de Uso (SRP) para la lectura de datos del Personal.
    """
    def __init__(self, db: AsyncSession):
        self.service = StaffService(db)

    async def get_staff(self, staff_id: uuid.UUID) -> Staff:
        """Query: Obtiene los detalles de un empleado por su ID."""
        staff = await self.service.get_by_id(staff_id)
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Miembro del personal no encontrado."
            )
        return staff

    async def get_staff_by_business(self, business_id: uuid.UUID) -> Sequence[Staff]:
        """Query: Lista todo el personal asignado a un negocio específico."""
        # Nota: Asegúrate de tener un método en StaffService que haga esta consulta al repositorio,
        # por ejemplo: `await self.staff_repo.get_by_business(business_id)`
        if hasattr(self.service, 'get_by_business'):
            return await self.service.get_business_staff(business_id)
        else:
            # Si aún no has implementado ese método en el servicio, levanta un error amistoso
            raise NotImplementedError("Falta implementar get_by_business en StaffService")