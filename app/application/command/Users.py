import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.AuthService import AuthService
from app.core.security.security import get_password_hash
from app.domain.models.models import User
from app.domain.schemas.users import UserCreate, UserUpdate
from app.infrastructure.repositories.user_repo import UserRepository


class UserCommands:
    """
    Agrupador de lógica de escritura para Usuarios.
    """
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.service = AuthService(db)
        

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
        return await self.service.create(new_user)

    async def update_profile(self, user_id: uuid.UUID, update_data: UserUpdate) -> User:
        """Command: Actualiza datos del perfil."""
        # 1. Obtenemos al usuario existente
        user = await self.service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        # 2. Si el usuario está intentando actualizar su email, validamos que no exista
        if update_data.email and update_data.email != user.email:
            existing_email = await self.repo.get_by_email(update_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este correo electrónico ya está en uso por otro usuario."
                )

        # 3. Guardamos los cambios. El BaseRepository automáticamente maneja el UserUpdate
        # e ignora los campos que sean None o que no se enviaron gracias a exclude_unset=True.
        return await self.service.update(user_id, update_data)
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        # 1. Verificamos que el usuario exista
        user = await self.service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        # 2. Llamamos al método delete del repositorio base
        success = await self.service.delete(user_id)
        
        # 3. Validamos si ocurrió algún error durante el borrado
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se pudo eliminar el usuario"
            )
        return True