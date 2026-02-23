from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.BaseService import BaseService
from app.core.security.security import create_access_token, verify_password
from app.core.security.SocialAuthService import SocialAuthService
from app.domain.models.models import User
from app.domain.schemas.auth import LoginRequest, SocialLoginRequest, Token
from app.domain.services.service import IAuthService
from app.infrastructure.repositories.user_repo import UserRepository


class AuthService(BaseService[User],IAuthService):
    """
    Implementación del servicio de autenticación siguiendo el contrato IAuthService.
    Se encarga de la validación de credenciales y la emisión de tokens JWT.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        # Inyectamos el repositorio para manejar la persistencia de usuarios
        self.user_repo = UserRepository(db)
        # Servicio core para validar tokens de Google/Apple/Facebook
        self.social_auth = SocialAuthService()

    async def authenticate_local(self, login_data: LoginRequest) -> Token:
        """
        Autenticación mediante teléfono y contraseña (flujo tradicional).
        """
        # Buscamos al usuario por su identificador principal (teléfono)
        user = await self.user_repo.get_by_phone(login_data.phone)
        
        # Validamos existencia y contraseña
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de acceso incorrectas."
            )
        
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de acceso incorrectas."
            )
            
        # Generamos el token de acceso para la sesión del usuario
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token)

    async def authenticate_social(self, data: SocialLoginRequest) -> Token:
        """
        Lógica de Login/Registro automático para proveedores sociales.
        Coordina la verificación externa y la sincronización con la base de datos local.
        """
        # 1. Validar el token con el proveedor (Google/Facebook/Apple)
        social_data = await self.social_auth.get_social_user(data.provider, data.id_token)
        if not social_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo validar la identidad con el proveedor externo."
            )

        # 2. Buscar si el usuario ya existe mediante su ID social único
        user = await self.user_repo.get_by_social_id(data.provider, social_data["social_id"])
        
        # 3. Si no existe por ID social, intentamos vincular por Email (si está disponible)
        if not user and social_data.get("email"):
            user = await self.user_repo.get_by_email(social_data["email"])
            if user:
                # El usuario ya existía; vinculamos la cuenta social para futuros inicios de sesión
                setattr(user, f"{data.provider.value}_id", social_data["social_id"])
                # Actualizamos datos opcionales
                user.full_name = user.full_name or social_data.get("full_name")
                user.image_url = user.image_url or social_data.get("image_url")
                await self.db.commit()

        # 4. Si el usuario sigue sin existir, lo registramos automáticamente (Registro Social)
        if not user:
            user = await self.user_repo.create_social_user(
                provider=data.provider,
                social_id=social_data["social_id"],
                email=social_data.get("email") or data.email,
                full_name=social_data.get("full_name") or data.full_name,
                phone=data.phone if hasattr(data, 'phone') else None,
                image_url=social_data.get("image_url"),
            )

        # 5. Emitir el JWT final de nuestra plataforma
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token)