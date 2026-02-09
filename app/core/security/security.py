from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto para el hashing de contraseñas usando Argon2 (más seguro que bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(
    subject: str | Any,
) -> str:
    """
    Genera un token JWT para un usuario específico.
    El 'subject' normalmente es el UUID del usuario.
    """
    
    expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña para su almacenamiento."""
    return pwd_context.hash(password)