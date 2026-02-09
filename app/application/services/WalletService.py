import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.BaseService import BaseService
from app.domain.models.models import TransactionType, Wallet, WalletTransaction
from app.domain.services.service import IWalletService
from app.infrastructure.repositories.wallet_repo import WalletRepository


class WalletService(BaseService[Wallet], IWalletService):
    """
    Servicio encargado de la gestión de saldos y transacciones financieras.
    Implementa la lógica de negocio para depósitos, retiros y consultas de saldo.
    """
    def __init__(self, db: AsyncSession):
        self.wallet_repo = WalletRepository(db)
        # Inicializamos el BaseService con el repositorio de Wallet para tener CRUD básico
        super().__init__(self.wallet_repo)

    async def get_or_create_wallet(self, user_id: uuid.UUID, business_id: uuid.UUID) -> Wallet:
        """
        Obtiene el monedero de un usuario para un negocio específico.
        Si no existe, lo crea automáticamente con saldo cero.
        """
        wallet = await self.wallet_repo.get_by_user_and_business(user_id, business_id)
        
        if not wallet:
            new_wallet = Wallet(
                user_id=user_id,
                business_id=business_id,
                balance=Decimal("0.00")
            )
            return await self.create(new_wallet)
            
        return wallet

    async def add_funds(
        self, 
        user_id: uuid.UUID, 
        business_id: uuid.UUID, 
        amount: Decimal, 
        description: str
    ) -> Wallet:
        """
        Modifica el saldo de un monedero (positivo para carga, negativo para cobro).
        Registra la transacción de auditoría obligatoria.
        """
        # 1. Recuperar (o crear) el monedero del usuario
        wallet = await self.get_or_create_wallet(user_id, business_id)
        
        # 2. Calcular nuevo saldo y validar que no quede en negativo
        new_balance = wallet.balance + amount
        if new_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente para realizar la operación."
            )

        # 3. Actualizar el balance del monedero
        # Usamos el método update del BaseService/Repository
        await self.update(wallet.id, {"balance": new_balance})

        # 4. Crear el registro de la transacción (Auditoría)
        # Determinamos el tipo basado en el signo del monto
        transaction_type = TransactionType.DEPOSIT if amount > 0 else TransactionType.WITHDRAWAL
        
        new_transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=abs(amount),
            type=transaction_type,
            description=description
        )
        
        # Guardamos la transacción a través del repositorio especializado
        await self.wallet_repo.add_transaction(new_transaction)
        
        # 5. Commit final para asegurar que tanto el balance como la transacción se guarden
        # Nota: wallet_repo.db es la misma sesión AsyncSession
        await self.wallet_repo.db.commit()
        await self.wallet_repo.db.refresh(wallet)
        
        return wallet