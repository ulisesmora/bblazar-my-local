import uuid
from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.domain.models.models import (
    RechargePlan,
    TransactionType,
    Wallet,
    WalletTransaction,
)
from app.domain.schemas.wallet import RechargePlanCreate
from app.infrastructure.repositories.base import BaseRepository


class WalletService(BaseService[Wallet]):
    """
    Servicio para gestionar el monedero digital de los usuarios y los planes de recarga.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_repo = BaseRepository(Wallet, db)
        self.transaction_repo = BaseRepository(WalletTransaction, db)
        self.plan_repo = BaseRepository(RechargePlan, db)
        
        super().__init__(self.wallet_repo)

    # ==========================================
    # LÓGICA DE MONEDEROS (WALLETS) Y TRANSACCIONES
    # ==========================================

    async def get_or_create_wallet(self, user_id: uuid.UUID, business_id: uuid.UUID) -> Wallet:
        """
        Busca el monedero de un usuario en un negocio. Si no existe, lo crea con saldo 0.
        """
        statement = select(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.business_id == business_id
        )
        result = await self.db.execute(statement)
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            new_wallet = Wallet(user_id=user_id, business_id=business_id, balance=Decimal("0.0"))
            wallet = await self.wallet_repo.create(new_wallet)
            
        return wallet

    async def add_funds(self, user_id: uuid.UUID, business_id: uuid.UUID, amount: Decimal, description: str, reference_id: uuid.UUID | None = None) -> Wallet:
        """Añade saldo a un monedero y registra la transacción (Ej. al comprar una recarga)."""
        if amount <= 0:
            raise ValueError("El monto a añadir debe ser mayor a cero.")
            
        wallet = await self.get_or_create_wallet(user_id, business_id)
        
        # 1. Registrar la transacción
        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            type=TransactionType.DEPOSIT,
            description=description,
            reference_id=reference_id
        )
        await self.transaction_repo.create(tx)
        
        # 2. Actualizar el saldo
        new_balance = wallet.balance + amount
        return await self.wallet_repo.update(wallet, {"balance": new_balance})

    async def deduct_funds(self, user_id: uuid.UUID, business_id: uuid.UUID, amount: Decimal, description: str, reference_id: uuid.UUID | None = None) -> Wallet:
        """Deduce saldo de un monedero (Ej. al pagar un pedido con el monedero)."""
        if amount <= 0:
            raise ValueError("El monto a deducir debe ser mayor a cero.")
            
        wallet = await self.get_or_create_wallet(user_id, business_id)
        
        if wallet.balance < amount:
            raise ValueError("Saldo insuficiente en el monedero.")
            
        # 1. Registrar la transacción (como un valor negativo o indicando tipo WITHDRAWAL)
        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,  # Guardamos el monto en positivo, pero el tipo indica la resta
            type=TransactionType.WITHDRAWAL,
            description=description,
            reference_id=reference_id
        )
        await self.transaction_repo.create(tx)
        
        # 2. Actualizar el saldo
        new_balance = wallet.balance - amount
        return await self.wallet_repo.update(wallet, {"balance": new_balance})

    async def get_wallet_transactions(self, wallet_id: uuid.UUID) -> Sequence[WalletTransaction]:
        """Obtiene el historial de movimientos de un monedero."""
        statement = select(WalletTransaction).where(
            WalletTransaction.wallet_id == wallet_id
        ).order_by(col(WalletTransaction.created_at).desc())
        
        result = await self.db.execute(statement)
        return result.scalars().all()

    # ==========================================
    # LÓGICA DE PLANES DE RECARGA (RECHARGE PLANS)
    # ==========================================

    async def create_recharge_plan(self, data: RechargePlanCreate) -> RechargePlan:
        """Crea un nuevo plan de recarga (Ej. Paga $100, recibe $120)."""
        new_plan = RechargePlan(**data.model_dump())
        return await self.plan_repo.create(new_plan)

    async def get_plans_by_business(self, business_id: uuid.UUID) -> Sequence[RechargePlan]:
        """Lista los planes activos de un negocio."""
        statement = select(RechargePlan).where(
            RechargePlan.business_id == business_id,
            RechargePlan.is_active == True,
            RechargePlan.deleted_at == None
        ).order_by(col(RechargePlan.price).asc())
        
        result = await self.db.execute(statement)
        return result.scalars().all()
        
    async def update_recharge_plan(self, plan_id: uuid.UUID, update_data: dict) -> RechargePlan:
        plan = await self.plan_repo.get(plan_id)
        if not plan:
            raise ValueError("Plan de recarga no encontrado")
        return await self.plan_repo.update(plan, update_data)

    async def delete_recharge_plan(self, plan_id: uuid.UUID) -> bool:
        plan = await self.plan_repo.get(plan_id)
        if not plan:
            raise ValueError("Plan de recarga no encontrado")
        return await self.plan_repo.delete(plan_id)