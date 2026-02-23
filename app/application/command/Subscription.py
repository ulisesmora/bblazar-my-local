import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.CatalogService import CatalogService
from app.application.services.SubscriptionsService import SubscriptionService
from app.domain.models.models import (
    Subscription,
    SubscriptionItem,
    SubscriptionPayment,
    SubscriptionStatus,
)
from app.domain.schemas.suscriptions import (
    SubscriptionCreate,
    SubscriptionStatusUpdate,
)


class SubscriptionCommands:
    """Caso de Uso (SRP) para la gestión del ciclo de vida de las suscripciones."""
    def __init__(self, db: AsyncSession):
        self.sub_service = SubscriptionService(db)
        self.catalog_service = CatalogService(db)

    async def subscribe(self, data: SubscriptionCreate) -> Subscription:
        """Command: Crea una nueva suscripción validando los planes en el catálogo."""
        sub_id = uuid.uuid4()
        sub_items = []
        
        # Para el ejemplo, asumimos un ciclo de facturación de 30 días
        now = datetime.now(UTC)
        period_end = now + timedelta(days=30)

        for entry in data.items:
            # Validar que el plan/producto exista
            item_db = await self.catalog_service.get_item_by_id(entry.item_id)
            if not item_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"El plan con ID {entry.item_id} no existe."
                )
            
            sub_items.append(
                SubscriptionItem(
                    subscription_id=sub_id, # Usamos el ID pre-generado
                    item_id=item_db.id,
                    quantity=entry.quantity,
                    unit_price=item_db.price
                )
            )
        
        # Construir cabecera de la suscripción
        new_sub = Subscription(
            id=sub_id, # ID pre-generado
            user_id=data.user_id,
            business_id=data.business_id,
            status=SubscriptionStatus.ACTIVE,
            current_period_end=period_end,
            frequency_days=(data.frequency_days), # <-- AÑADIDO
            pickup_time=data.pickup_time
        )

        return await self.sub_service.create_full_subscription(new_sub, sub_items)

    async def update_status(self, sub_id: uuid.UUID, data: SubscriptionStatusUpdate) -> Subscription:
        """Command: Actualiza el estado (Ideal para webhooks de Stripe)."""
        try:
            return await self.sub_service.update_status(sub_id, data.status, data.current_period_end)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    async def register_payment(self, sub_id: uuid.UUID, amount: Decimal, payment_status: str, external_ref: str | None = None) -> SubscriptionPayment:
        """Command: Deja constancia de un intento de cobro recurrente."""
        payment_data = {
            "subscription_id": sub_id,
            "amount": amount,
            "status": payment_status,
            "payment_date": datetime.now(UTC),
            "external_reference": external_ref
        }
        return await self.sub_service.record_payment(payment_data)