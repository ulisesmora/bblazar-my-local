import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# --- CORRECCIÓN DE RUTA ---
# Añade la raíz del proyecto al path de Python para que encuentre el módulo 'app'
root_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_path))

# Importaciones de la aplicación
from app.core.config import settings
from app.domain.models.models import SQLModel

# Interpretamos el archivo de configuración para el registro de logs
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Asignamos los metadatos de los modelos
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """
    Función auxiliar para ejecutar las migraciones en un contexto síncrono
    dentro de la conexión asíncrona.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """
    Crea el motor asíncrono y orquesta la ejecución de migraciones
    usando run_sync para manejar el driver asyncpg.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online'."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()