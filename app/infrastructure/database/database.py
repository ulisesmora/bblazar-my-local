from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

# Motor de base de datos asíncrono para PostgreSQL
# Se utiliza la URL configurada en los settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Constructor de sesiones asíncronas (async_sessionmaker es el estándar para SQLAlchemy 2.0+)
# Esto resuelve el error de sobrecarga en el __init__
async_session = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_db():
    """Inicializa las tablas en la base de datos (usar solo en desarrollo)"""
    async with engine.begin() as conn:
        # En producción se recomienda usar Alembic para migraciones
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para inyectar la sesión en los endpoints de FastAPI.
    Se utiliza AsyncGenerator para indicar que la función usa 'yield'.
    """
    async with async_session() as session:
        yield session