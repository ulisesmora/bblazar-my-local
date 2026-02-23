import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.command.Order import OrderCommands
from app.application.query.Order import OrderQueries
from app.domain.models.models import OrderStatus
from app.domain.schemas.orders import OrderCreate, OrderRead, OrderStatusUpdate
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# QUERIES (Lecturas - GET)
# ==========================================

@router.get("/business/{business_id}", response_model=list[OrderRead], status_code=status.HTTP_200_OK)
async def get_orders_by_business(
    business_id: uuid.UUID, 
    status_filter: OrderStatus | None = Query(None, description="Filtrar por estado del pedido"),
    db: AsyncSession = Depends(get_session)
):
    """Lista pedidos de un negocio. Opcionalmente filtrables por estado (ej. PENDING)."""
    queries = OrderQueries(db)
    return await queries.get_business_orders(business_id, status_filter)

@router.get("/user/{user_id}", response_model=list[OrderRead], status_code=status.HTTP_200_OK)
async def get_orders_by_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Historial completo de compras de un cliente específico."""
    queries = OrderQueries(db)
    return await queries.get_user_orders(user_id)

@router.get("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene el detalle completo de un pedido, incluyendo los productos comprados."""
    queries = OrderQueries(db)
    return await queries.get_order_details(order_id)


# ==========================================
# COMMANDS (Escrituras - POST, PATCH)
# ==========================================

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_new_order(order_in: OrderCreate, db: AsyncSession = Depends(get_session)):
    """
    Crea un pedido. 
    Este endpoint orquesta la validación de stock y el cobro automático desde el monedero.
    """
    commands = OrderCommands(db)
    return await commands.create_order(order_in)

@router.patch("/{order_id}/status", response_model=OrderRead, status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: uuid.UUID, 
    status_in: OrderStatusUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """Actualiza el estado de un pedido (Ej. cambiar de PENDING a PREPARING o COMPLETED)."""
    commands = OrderCommands(db)
    return await commands.update_status(order_id, status_in)