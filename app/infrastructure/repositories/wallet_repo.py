import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.domain.models.models import Wallet, WalletTransaction
from app.domain.repositories.repositories import IWalletRepository
from app.infrastructure.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet], IWalletRepository):
    """
    Repositorio para gestionar saldos y transacciones de monederos.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Wallet, db)

    async def get_by_user_and_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Wallet | None:
        """
        Busca el monedero específico de un usuario para un negocio determinado.
        Recordemos que en este SaaS, el saldo es por negocio (aislado).
        """
        statement = select(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.business_id == business_id
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_transactions(
        self, wallet_id: uuid.UUID, limit: int = 20
    ) -> Sequence[WalletTransaction]:
        """
        Obtiene el historial de transacciones de un monedero específico.
        Se utiliza la función desc() de sqlalchemy para evitar errores de tipado en Pylance.
        """
        statement = (
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet_id)
            .order_by(col(WalletTransaction.created_at).desc())
        )
        
        result = await self.db.execute(statement)
        # Aplicamos el límite después de obtener los escalares
        return result.scalars().all()[:limit]

    async def add_transaction(self, transaction: WalletTransaction) -> WalletTransaction:
        """
        Registra una nueva transacción de auditoría.
        """
        self.db.add(transaction)
        # No hacemos commit aquí porque usualmente esto es parte de una 
        # operación mayor (ej: actualizar el saldo y registrar la carga).
        return transaction