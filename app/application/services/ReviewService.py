import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.domain.models.models import ItemReview, OrderReview, StaffReview
from app.domain.services.service import IReviewService
from app.infrastructure.repositories.base import BaseRepository


class ReviewService(IReviewService):
    """
    Servicio encargado de gestionar las calificaciones logísticas, 
    de productos y de personal.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_review_repo = BaseRepository(OrderReview, db)
        self.item_review_repo = BaseRepository(ItemReview, db)
        self.staff_review_repo = BaseRepository(StaffReview, db)

    # --- ORDER REVIEWS ---
    async def create_order_review(self, review: OrderReview) -> OrderReview:
        """Crea la reseña del pedido. Valida la restricción unique=True del order_id."""
        statement = select(OrderReview).where(OrderReview.order_id == review.order_id)
        existing = (await self.db.execute(statement)).scalar_one_or_none()
        if existing:
            raise ValueError("Ya existe una reseña general para este pedido.")
            
        return await self.order_review_repo.create(review)

    async def get_business_reviews(self, business_id: uuid.UUID) -> Sequence[OrderReview]:
        statement = (
            select(OrderReview)
            .where(OrderReview.business_id == business_id)
            .order_by(col(OrderReview.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    # --- ITEM REVIEWS ---
    async def create_item_review(self, review: ItemReview) -> ItemReview:
        return await self.item_review_repo.create(review)

    async def get_item_reviews(self, item_id: uuid.UUID) -> Sequence[ItemReview]:
        statement = (
            select(ItemReview)
            .where(ItemReview.item_id == item_id)
            .order_by(col(ItemReview.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    # --- STAFF REVIEWS ---
    async def create_staff_review(self, review: StaffReview) -> StaffReview:
        return await self.staff_review_repo.create(review)

    async def get_staff_reviews(self, staff_id: uuid.UUID) -> Sequence[StaffReview]:
        statement = (
            select(StaffReview)
            .where(StaffReview.staff_id == staff_id)
            .order_by(col(StaffReview.created_at).desc())
        )
        result = await self.db.execute(statement)
        return result.scalars().all()