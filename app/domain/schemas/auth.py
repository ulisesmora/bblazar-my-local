
from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.models.models import SocialProvider


class Token(BaseModel):
    """
    Estructura de respuesta cuando un usuario se autentica con éxito.
    """
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)

class TokenPayload(BaseModel):
    """
    Representa los datos internos (claims) del JWT.
    El campo 'sub' (subject) contiene normalmente el ID del usuario.
    """
    sub: str | None = None
    exp: int | None = None

class LoginRequest(BaseModel):
    """
    Datos requeridos para el inicio de sesión tradicional.
    """
    phone: str
    password: str

class SocialLoginRequest(BaseModel):
    """
    Datos requeridos para la autenticación con terceros (Google, Apple, Facebook).
    """
    provider: SocialProvider
    id_token: str
    email: EmailStr | None = None
    full_name: str | None = None
    phone: str | None = None