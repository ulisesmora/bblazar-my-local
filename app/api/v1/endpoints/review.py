import uuid

# Commands y Queries
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

# Schemas
from app.application.command.Review import ReviewCommands
from app.application.query.Review import ReviewQueries
from app.domain.schemas.reviews import (
    ItemReviewCreate,
    ItemReviewRead,
    OrderReviewCreate,
    OrderReviewRead,
    StaffReviewCreate,
    StaffReviewRead,
)

# Dependencia de la base de datos
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# RUTAS DE ORDER REVIEWS (Negocio/Logística)
# ==========================================

@router.post("/order", response_model=OrderReviewRead, status_code=status.HTTP_201_CREATED)
async def create_order_review(review_in: OrderReviewCreate, db: AsyncSession = Depends(get_session)):
    """Evalúa la experiencia general del pedido, velocidad, atención y ubicación."""
    commands = ReviewCommands(db)
    return await commands.create_order_review(review_in)

@router.get("/business/{business_id}", response_model=list[OrderReviewRead], status_code=status.HTTP_200_OK)
async def get_business_reviews(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene las reseñas generales asociadas a un negocio."""
    queries = ReviewQueries(db)
    return await queries.get_business_reviews(business_id)

# ==========================================
# RUTAS DE ITEM REVIEWS (Productos/Servicios)
# ==========================================

@router.post("/item", response_model=ItemReviewRead, status_code=status.HTTP_201_CREATED)
async def create_item_review(review_in: ItemReviewCreate, db: AsyncSession = Depends(get_session)):
    """Evalúa la calidad específica de un producto o servicio comprado."""
    commands = ReviewCommands(db)
    return await commands.create_item_review(review_in)

@router.get("/item/{item_id}", response_model=list[ItemReviewRead], status_code=status.HTTP_200_OK)
async def get_item_reviews(item_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene las reseñas específicas de un artículo del catálogo."""
    queries = ReviewQueries(db)
    return await queries.get_item_reviews(item_id)

# ==========================================
# RUTAS DE STAFF REVIEWS (Personal)
# ==========================================

@router.post("/staff", response_model=StaffReviewRead, status_code=status.HTTP_201_CREATED)
async def create_staff_review(review_in: StaffReviewCreate, db: AsyncSession = Depends(get_session)):
    """Evalúa el trato y profesionalismo de un miembro del staff."""
    commands = ReviewCommands(db)
    return await commands.create_staff_review(review_in)

@router.get("/staff/{staff_id}", response_model=list[StaffReviewRead], status_code=status.HTTP_200_OK)
async def get_staff_reviews(staff_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene las calificaciones de un empleado/profesional."""
    queries = ReviewQueries(db)
    return await queries.get_staff_reviews(staff_id)