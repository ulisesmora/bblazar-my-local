from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.ReviewService import ReviewService
from app.domain.models.models import ItemReview, OrderReview, StaffReview
from app.domain.schemas.reviews import (
    ItemReviewCreate,
    OrderReviewCreate,
    StaffReviewCreate,
)


class ReviewCommands:
    """
    Caso de Uso (SRP) para la creación de los distintos tipos de reseñas.
    """
    def __init__(self, db: AsyncSession):
        self.service = ReviewService(db)

    async def create_order_review(self, data: OrderReviewCreate) -> OrderReview:
        """Command: Crea una reseña logística del pedido. Falla si el pedido ya fue reseñado."""
        try:
            new_review = OrderReview(**data.model_dump())
            return await self.service.create_order_review(new_review)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
            )

    async def create_item_review(self, data: ItemReviewCreate) -> ItemReview:
        """Command: Crea una reseña sobre la calidad de un producto."""
        new_review = ItemReview(**data.model_dump())
        return await self.service.create_item_review(new_review)

    async def create_staff_review(self, data: StaffReviewCreate) -> StaffReview:
        """Command: Crea una reseña evaluando la atención de un miembro del equipo."""
        new_review = StaffReview(**data.model_dump())
        return await self.service.create_staff_review(new_review)