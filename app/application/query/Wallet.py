import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.WalletService import WalletService
from app.domain.models.models import RechargePlan, Wallet, WalletTransaction


class WalletQueries:
    """Caso de Uso (SRP) para consultar saldos y movimientos."""
    def __init__(self, db: AsyncSession):
        self.service = WalletService(db)

    async def get_user_balance(self, user_id: uuid.UUID, business_id: uuid.UUID) -> Wallet:
        """Query: Obtiene el saldo actual de un usuario en un negocio (o lo crea en 0)."""
        return await self.service.get_or_create_wallet(user_id, business_id)

    async def get_transaction_history(self, wallet_id: uuid.UUID) -> Sequence[WalletTransaction]:
        """Query: Obtiene el libro mayor de movimientos de un monedero."""
        return await self.service.get_wallet_transactions(wallet_id)

    async def get_active_recharge_plans(self, business_id: uuid.UUID) -> Sequence[RechargePlan]:
        """Query: Lista los planes de recarga disponibles para comprar en un negocio."""
        return await self.service.get_plans_by_business(business_id)