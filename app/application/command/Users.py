import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.security import get_password_hash
from app.domain.models.models import User
from app.domain.schemas.users import UserCreate
from app.infrastructure.repositories.user_repo import UserRepository


class UserCommands:
    """
    Agrupador de lógica de escritura para Usuarios.
    """
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register_user(self, data: UserCreate) -> User:
        """
        Command: Registra un usuario nuevo.
        Lógica: Validar duplicados, hashear password y persistir.
        """
        existing_phone = await self.repo.get_by_phone(data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de teléfono ya existe."
            )
            
        new_user = User(
            phone=data.phone,
            email=data.email,
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
            role=data.role
        )
        return await self.repo.create(new_user)

    async def update_profile(self, user_id: uuid.UUID, update_data: dict) -> User:
        """Command: Actualiza datos del perfil."""
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return await self.repo.update(user, update_data)