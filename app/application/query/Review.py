import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.ReviewService import ReviewService
from app.domain.models.models import ItemReview, OrderReview, StaffReview


class ReviewQueries:
    """
    Caso de Uso (SRP) para consultar las calificaciones y comentarios.
    """
    def __init__(self, db: AsyncSession):
        self.service = ReviewService(db)

    async def get_business_reviews(self, business_id: uuid.UUID) -> Sequence[OrderReview]:
        """Query: Lista las reseñas generales que tiene un negocio (logística/atención/ubicación)."""
        return await self.service.get_business_reviews(business_id)

    async def get_item_reviews(self, item_id: uuid.UUID) -> Sequence[ItemReview]:
        """Query: Lista las reseñas específicas sobre la calidad de un producto del catálogo."""
        return await self.service.get_item_reviews(item_id)

    async def get_staff_reviews(self, staff_id: uuid.UUID) -> Sequence[StaffReview]:
        """Query: Lista las reseñas directas hacia un profesional (barbero, entrenador, etc)."""
        return await self.service.get_staff_reviews(staff_id)