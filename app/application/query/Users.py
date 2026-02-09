import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import User
from app.infrastructure.repositories.user_repo import UserRepository


class UserQueries:
    """
    Agrupador de lógica de lectura para Usuarios.
    Optimizado para devolver datos rápidamente sin lógica de validación pesada.
    """
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Query: Obtiene un usuario por ID."""
        return await self.repo.get(user_id)

    async def get_by_phone(self, phone: str) -> User | None:
        """Query: Busca por teléfono."""
        return await self.repo.get_by_phone(phone)

    async def list_active_users(self) -> Sequence[User] | None:
        """Query: Lista usuarios que no han sido borrados lógicamente."""
        return await self.repo.list_all()