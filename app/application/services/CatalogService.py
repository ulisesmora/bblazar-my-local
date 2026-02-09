import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.application.services.BaseService import BaseService
from app.domain.models.models import Category, Item
from app.domain.schemas.category import CategoryCreate, ItemCreate
from app.domain.services.service import ICatalogService
from app.infrastructure.repositories.base import BaseRepository


class CatalogService(BaseService[Item], ICatalogService):
    """
    Servicio encargado de la gestión del catálogo (Categorías y Productos/Servicios).
    Hereda de BaseService[Item] para tener CRUD completo de productos automáticamente.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        # Repositorio para Items (Productos/Servicios)
        self.item_repo = BaseRepository(Item, db)
        # Repositorio para Categorías
        self.category_repo = BaseRepository(Category, db)
        
        # Inicializamos el BaseService con el repositorio de Items
        super().__init__(self.item_repo)

    # --- Lógica de Categorías ---

    async def create_category(self, data: CategoryCreate) -> Category:
        """
        Crea una nueva categoría para organizar el menú del negocio.
        """
        new_category = Category(**data.model_dump())
        return await self.category_repo.create(new_category)

    async def get_categories_by_business(self, business_id: uuid.UUID) -> Sequence[Category]:
        """
        Obtiene todas las categorías pertenecientes a un negocio específico.
        """
        statement = select(Category).where(
            Category.business_id == business_id,
            Category.deleted_at == None
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    # --- Lógica de Items (Productos/Servicios) ---

    async def create_item(self, data: ItemCreate) -> Item:
        """
        Registra un nuevo producto o servicio en el catálogo.
        """
        new_item = Item(**data.model_dump())
        return await self.item_repo.create(new_item)

    async def get_items_by_business(self, business_id: uuid.UUID) -> Sequence[Item]:
        """
        Obtiene el listado completo de productos/servicios de un negocio.
        """
        statement = select(Item).where(
            Item.business_id == business_id,
            Item.deleted_at == None
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_items_by_category(self, category_id: uuid.UUID) -> Sequence[Item]:
        """
        Filtra productos por una categoría específica.
        """
        statement = select(Item).where(
            Item.category_id == category_id,
            Item.deleted_at == None
        )
        result = await self.db.execute(statement)
        return result.scalars().all()