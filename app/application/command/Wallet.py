import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.WalletService import WalletService
from app.domain.models.models import RechargePlan, Wallet
from app.domain.schemas.wallet import RechargePlanCreate, RechargePlanUpdate


class WalletCommands:
    """Caso de Uso (SRP) para la escritura de datos financieros."""
    def __init__(self, db: AsyncSession):
        self.service = WalletService(db)

    # --- MOVIMIENTOS DE SALDO ---

    async def deposit_funds(self, user_id: uuid.UUID, business_id: uuid.UUID, amount: Decimal, description: str, reference_id: uuid.UUID | None = None) -> Wallet:
        """Command: Añade saldo al monedero del usuario."""
        try:
            return await self.service.add_funds(user_id, business_id, amount, description, reference_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def withdraw_funds(self, user_id: uuid.UUID, business_id: uuid.UUID, amount: Decimal, description: str, reference_id: uuid.UUID | None = None) -> Wallet:
        """Command: Deduce saldo (Ej. para pagar un pedido)."""
        try:
            return await self.service.deduct_funds(user_id, business_id, amount, description, reference_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # --- PLANES DE RECARGA ---

    async def create_plan(self, data: RechargePlanCreate) -> RechargePlan:
        """Command: Crea un nuevo plan de recarga."""
        return await self.service.create_recharge_plan(data)

    async def update_plan(self, plan_id: uuid.UUID, update_data: RechargePlanUpdate) -> RechargePlan:
        """Command: Actualiza precio, crédito o estado de un plan."""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            return await self.service.update_recharge_plan(plan_id, update_dict)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def delete_plan(self, plan_id: uuid.UUID) -> bool:
        """Command: Elimina lógicamente un plan de recarga."""
        try:
            return await self.service.delete_recharge_plan(plan_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))