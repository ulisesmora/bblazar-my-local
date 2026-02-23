import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.SubscriptionsService import SubscriptionService
from app.domain.models.models import Subscription


class SubscriptionQueries:
    """
    Caso de Uso (SRP) para consultar suscripciones y membresías.
    Solo lectura, sin modificar el estado de la base de datos.
    """
    def __init__(self, db: AsyncSession):
        self.service = SubscriptionService(db)

    async def get_subscription_details(self, sub_id: uuid.UUID) -> Subscription:
        """Query: Obtiene una suscripción y sus planes/productos incluidos."""
        sub = await self.service.get_subscription_with_items(sub_id)
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Suscripción no encontrada."
            )
        return sub

    async def get_user_history(self, user_id: uuid.UUID) -> Sequence[Subscription]:
        """Query: Lista todas las membresías (activas, canceladas o pasadas) de un cliente."""
        return await self.service.get_user_subscriptions(user_id)

    async def get_business_active_subs(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[Subscription]:
        """Query: Lista las membresías de un negocio (Ideal para paneles de administración y calcular ingresos recurrentes)."""
        return await self.service.get_business_subscriptions(business_id, active_only)