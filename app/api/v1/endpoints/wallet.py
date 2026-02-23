import uuid
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.command.Wallet import WalletCommands
from app.application.query.Wallet import WalletQueries
from app.domain.schemas.wallet import (
    RechargePlanCreate,
    RechargePlanRead,
    RechargePlanUpdate,
    TransactionRead,
    WalletRead,
)

# Dependencia de DB
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# RUTAS DEL MONEDERO Y TRANSACCIONES
# ==========================================

@router.get("/balance", response_model=WalletRead, status_code=status.HTTP_200_OK)
async def get_wallet_balance(
    user_id: uuid.UUID = Query(...), 
    business_id: uuid.UUID = Query(...), 
    db: AsyncSession = Depends(get_session)
):
    """Obtiene el saldo disponible de un usuario en un negocio específico."""
    queries = WalletQueries(db)
    return await queries.get_user_balance(user_id, business_id)

@router.get("/{wallet_id}/transactions", response_model=list[TransactionRead], status_code=status.HTTP_200_OK)
async def get_transactions(wallet_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene el historial contable de recargas y gastos del monedero."""
    queries = WalletQueries(db)
    return await queries.get_transaction_history(wallet_id)

@router.post("/deposit", response_model=WalletRead, status_code=status.HTTP_200_OK)
async def deposit_funds(
    user_id: uuid.UUID = Body(...),
    business_id: uuid.UUID = Body(...),
    amount: Decimal = Body(...),
    description: str = Body(...),
    reference_id: uuid.UUID | None = Body(None),
    db: AsyncSession = Depends(get_session)
):
    """Añade fondos al monedero (Uso interno / Webhooks de pagos)."""
    commands = WalletCommands(db)
    return await commands.deposit_funds(user_id, business_id, amount, description, reference_id)

@router.post("/withdraw", response_model=WalletRead, status_code=status.HTTP_200_OK)
async def withdraw_funds(
    user_id: uuid.UUID = Body(...),
    business_id: uuid.UUID = Body(...),
    amount: Decimal = Body(...),
    description: str = Body(...),
    reference_id: uuid.UUID | None = Body(None),
    db: AsyncSession = Depends(get_session)
):
    """Deduce fondos del monedero (Ej. al confirmar un pedido con saldo a favor)."""
    commands = WalletCommands(db)
    return await commands.withdraw_funds(user_id, business_id, amount, description, reference_id)


# ==========================================
# RUTAS DE PLANES DE RECARGA
# ==========================================

@router.get("/plans/business/{business_id}", response_model=list[RechargePlanRead], status_code=status.HTTP_200_OK)
async def get_recharge_plans(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Lista todos los planes de recarga activos configurados por el negocio."""
    queries = WalletQueries(db)
    return await queries.get_active_recharge_plans(business_id)

@router.post("/plans", response_model=RechargePlanRead, status_code=status.HTTP_201_CREATED)
async def create_recharge_plan(plan_in: RechargePlanCreate, db: AsyncSession = Depends(get_session)):
    """Crea un nuevo paquete de recarga (Ej. Paga $100 y recibe $120)."""
    commands = WalletCommands(db)
    return await commands.create_plan(plan_in)

@router.patch("/plans/{plan_id}", response_model=RechargePlanRead, status_code=status.HTTP_200_OK)
async def update_recharge_plan(plan_id: uuid.UUID, plan_in: RechargePlanUpdate, db: AsyncSession = Depends(get_session)):
    """Actualiza los valores de un paquete de recarga."""
    commands = WalletCommands(db)
    return await commands.update_plan(plan_id, plan_in)

@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recharge_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina (soft delete) un paquete de recarga."""
    commands = WalletCommands(db)
    await commands.delete_plan(plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)