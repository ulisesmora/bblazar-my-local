import uuid
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# Dependencia de la base de datos
from app.application.command.Subscription import SubscriptionCommands
from app.application.query.Subscription import SubscriptionQueries
from app.domain.schemas.suscriptions import (
    SubscriptionCreate,
    SubscriptionPaymentRead,
    SubscriptionRead,
    SubscriptionStatusUpdate,
)
from app.infrastructure.database.database import get_session

router = APIRouter()


@router.get("/user/{user_id}", response_model=list[SubscriptionRead], status_code=status.HTTP_200_OK)
async def get_user_subscriptions(user_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    queries = SubscriptionQueries(db)
    return await queries.get_user_history(user_id)

@router.get("/business/{business_id}", response_model=list[SubscriptionRead], status_code=status.HTTP_200_OK)
async def get_business_subscriptions(
    business_id: uuid.UUID, 
    active_only: bool = Query(True, description="Filtrar para ver solo suscripciones activas"),
    db: AsyncSession = Depends(get_session)
):
    """Lista las membresías de un negocio (Ideal para calcular entregas recurrentes y MRR)."""
    queries = SubscriptionQueries(db)
    return await queries.get_business_active_subs(business_id, active_only)

@router.get("/{sub_id}", response_model=SubscriptionRead, status_code=status.HTTP_200_OK)
async def get_subscription(sub_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Detalle completo de una suscripción particular y sus productos/planes."""
    queries = SubscriptionQueries(db)
    return await queries.get_subscription_details(sub_id)


# ==========================================
# COMMANDS (Escrituras - POST, PATCH)
# ==========================================

@router.post("/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
async def create_subscription(sub_in: SubscriptionCreate, db: AsyncSession = Depends(get_session)):
    commands = SubscriptionCommands(db)
    return await commands.subscribe(sub_in)

@router.patch("/{sub_id}/status", response_model=SubscriptionRead, status_code=status.HTTP_200_OK)
async def update_subscription_status(
    sub_id: uuid.UUID, 
    status_in: SubscriptionStatusUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """
    Actualiza el estado (ej. active, canceled, past_due). 
    Ideal para ser llamado por Webhooks de pasarelas de pago.
    """
    commands = SubscriptionCommands(db)
    return await commands.update_status(sub_id, status_in)

@router.post("/{sub_id}/payments", response_model=SubscriptionPaymentRead, status_code=status.HTTP_201_CREATED)
async def record_payment_attempt(
    sub_id: uuid.UUID,
    amount: Decimal = Body(..., description="Monto cobrado/intentado"),
    payment_status: str = Body(..., description="Estado del pago (succeeded, failed, etc.)"),
    external_reference: str | None = Body(None, description="ID de transacción en Stripe/MercadoPago"),
    db: AsyncSession = Depends(get_session)
):
    """Deja constancia de un pago (exitoso o fallido) en el historial de la suscripción."""
    commands = SubscriptionCommands(db)
    return await commands.register_payment(sub_id, amount, payment_status, external_reference)