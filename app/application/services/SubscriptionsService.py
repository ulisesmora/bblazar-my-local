import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from app.application.services.BaseService import BaseService
from app.domain.models.models import Subscription, SubscriptionItem, SubscriptionPayment
from app.domain.services.service import ISubscriptionService
from app.infrastructure.repositories.base import BaseRepository


class SubscriptionService(BaseService[Subscription], ISubscriptionService):
    """
    Servicio para gestionar el ciclo de vida de las suscripciones y su historial de pagos.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_repo = BaseRepository(Subscription, db)
        self.item_repo = BaseRepository(SubscriptionItem, db)
        self.payment_repo = BaseRepository(SubscriptionPayment, db)
        super().__init__(self.subscription_repo)

    async def create_full_subscription(self, new_subscription: Subscription, items: list[SubscriptionItem]) -> Subscription:
        """
        Guarda la cabecera de la suscripción y sus detalles atómicamente.
        """
        saved_sub = await self.subscription_repo.create(new_subscription)
        
        for item in items:
            await self.item_repo.create(item)
            
        return await self.get_subscription_with_items(saved_sub.id) # type: ignore

    async def get_subscription_with_items(self, subscription_id: uuid.UUID) -> Subscription | None:
        """Obtiene una suscripción incluyendo sus planes/items."""
        statement = select(Subscription).where(
            Subscription.id == subscription_id
        ).options(selectinload(Subscription.items)) # type: ignore
        
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def update_status(self, subscription_id: uuid.UUID, new_status: str, period_end: datetime | None = None) -> Subscription:
        """
        Actualiza el estado de la suscripción (Ej. cuando un Webhook de Stripe avisa de un pago fallido).
        """
        subscription = await self.subscription_repo.get(subscription_id)
        if not subscription:
            raise ValueError("Suscripción no encontrada.")
            
        update_data: dict[str, Any] = {"status": new_status}
        if period_end:
            update_data["current_period_end"] = period_end
            
        return await self.subscription_repo.update(subscription, update_data)

    async def record_payment(self, payment_data: dict) -> SubscriptionPayment:
        """Registra un cobro exitoso o fallido de una suscripción."""
        new_payment = SubscriptionPayment(**payment_data)
        return await self.payment_repo.create(new_payment)

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> Sequence[Subscription]:
        """Obtiene todas las suscripciones activas o pasadas de un usuario."""
        statement = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .options(selectinload(Subscription.items)) # type: ignore
            .order_by(col(Subscription.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_business_subscriptions(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[Subscription]:
        """Obtiene las suscripciones de un negocio (Ideal para métricas de MRR)."""
        statement = select(Subscription).where(Subscription.business_id == business_id)
        
        if active_only:
            statement = statement.where(Subscription.status == "active")
            
        statement = statement.options(selectinload(Subscription.items)).order_by(col(Subscription.created_at).desc()) # type: ignore
        result = await self.db.execute(statement)
        return result.scalars().all()