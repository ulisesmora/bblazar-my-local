import logging
import time
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.endpoints import users
from app.core.config import settings
from app.infrastructure.database.database import engine

# Configuración de logs profesional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Verifica que la infraestructura crítica esté disponible al arrancar.
    """
    logger.info(f"=== INICIANDO {settings.PROJECT_NAME} ===")
    
    # Verificación de salud de la base de datos
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Conexión a PostgreSQL: OK")
    except Exception as e:
        logger.error(f"❌ Fallo en la conexión inicial de DB: {e}")
    
    yield
    logger.info(f"=== CERRANDO {settings.PROJECT_NAME} ===")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- MIDDLEWARES ---

# 1. CORS: Permite la comunicación con el Frontend y aplicaciones móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, definir dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rastreo y Diagnóstico: Monitorea el rendimiento de cada petición
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"⬇️ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"⬆️ {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)")
        return response
    except Exception as e:
        logger.error(f"❌ Error crítico en pipeline: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"}
        )

# --- ENDPOINTS DE SALUD ---

@app.get("/", tags=["Health"])
async def root():
    """Información básica de la API."""
    return {
        "status": "online",
        "server": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica la salud de la API y sus dependencias."""
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"
        
    return {
        "status": "ok",
        "server": "granian",
        "database": db_status,
        "timestamp": time.time()
    }



api_router = APIRouter()

# Configuración modular de rutas con sus respectivos tags para la documentación OpenAPI
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["Identidad y Usuarios"]
)


app.include_router(api_router, prefix=settings.API_V1_STR)
