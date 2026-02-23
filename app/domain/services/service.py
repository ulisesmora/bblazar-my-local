import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from app.domain.models.models import (
    Business,
    Category,
    DailyInventory,
    Item,
    ItemReview,
    KnowledgeSource,
    Order,
    OrderItem,
    OrderReview,
    OrderStatus,
    Staff,
    StaffReview,
    Subscription,
    SubscriptionItem,
    SubscriptionPayment,
    Wallet,
)
from app.domain.schemas.auth import LoginRequest, SocialLoginRequest, Token
from app.domain.schemas.business import BusinessCreate
from app.domain.schemas.category import CategoryCreate, ItemCreate

ModelType = TypeVar("ModelType")


class IService(ABC, Generic[ModelType]):
    """
    Contrato base para servicios que exponen operaciones CRUD completas.
    Incluye soporte para creación, actualización y eliminación (soft delete).
    """
    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        pass

    @abstractmethod
    async def list_all(self) -> Sequence[ModelType] | None:
        pass

    @abstractmethod
    async def create(self, data: Any) -> ModelType:
        pass

    @abstractmethod
    async def update(self, id: uuid.UUID, data: Any) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        """
        Elimina un registro por ID. 
        La implementación debe decidir si aplica soft delete o borrado físico.
        """
        pass
    

class IAuthService(ABC):
    """
    Interfaz para el servicio de autenticación.
    Define el contrato que cualquier implementación de seguridad debe cumplir.
    """
    @abstractmethod
    async def authenticate_local(self, login_data: LoginRequest) -> Token:
        pass

    @abstractmethod
    async def authenticate_social(self, data: SocialLoginRequest) -> Token:
        pass
    


class IBusinessService(ABC):
    """
    Contrato para la gestión de locales y configuración de multi-tenancy.
    """
    @abstractmethod
    async def register_business(self, data: BusinessCreate) -> Business:
        pass

    @abstractmethod
    async def get_owner_businesses(self, owner_id: uuid.UUID) -> Sequence[Business]:
        pass

    @abstractmethod
    async def get_business_by_slug(self, slug: str) -> Business:
        pass

    @abstractmethod
    async def update_mcp_config(
        self, business_id: uuid.UUID, prompt: str, bot_name: str
    ) -> Business:
        pass

class IWalletService(ABC):
    """
    Contrato para la gestión financiera, saldos y auditoría de transacciones.
    """
    @abstractmethod
    async def get_or_create_wallet(self, user_id: uuid.UUID, business_id: uuid.UUID) -> Wallet:
        pass

    @abstractmethod
    async def add_funds(
        self, user_id: uuid.UUID, business_id: uuid.UUID, amount: Decimal, description: str
    ) -> Wallet:
        pass
    
class ICatalogService(ABC):
    """
    Contrato para la gestión del catálogo.
    Define las operaciones que CatalogService DEBE implementar.
    """
    @abstractmethod
    async def create_category(self, data: CategoryCreate) -> Category:
        pass

    @abstractmethod
    async def get_categories_by_business(self, business_id: uuid.UUID) -> Sequence[Category]:
        pass

    @abstractmethod
    async def create_item(self, data: ItemCreate) -> Item:
        pass

    @abstractmethod
    async def get_items_by_business(self, business_id: uuid.UUID) -> Sequence[Item]:
        pass

    @abstractmethod
    async def get_items_by_category(self, category_id: uuid.UUID) -> Sequence[Item]:
        pass
    


class IInventoryService(ABC):
    """
    Contrato para la gestión de inventario diario.
    No es un CRUD simple porque requiere lógica de fechas y cálculos de disponibilidad.
    """
    @abstractmethod
    async def set_daily_stock(self, item_id: uuid.UUID, target_date: date, quantity: int)  -> DailyInventory :
        """Establece la cantidad producida/disponible para un día específico."""
        pass

    @abstractmethod
    async def check_availability(self, item_id: uuid.UUID, target_date: date, requested_qty: int) -> bool:
        """Verifica si existe stock suficiente antes de procesar una orden."""
        pass
class IOrderService(ABC):
    """
    Contrato para el servicio de Pedidos.
    Define las operaciones exclusivas de base de datos para la entidad Order.
    """
    
    @abstractmethod
    async def save_full_order(self, new_order: Order, items: list[OrderItem]) -> Order:
        """Guarda la cabecera del pedido y sus líneas de detalle atómicamente."""
        pass

    @abstractmethod
    async def get_order_with_items(self, order_id: uuid.UUID) -> Order | None:
        """Obtiene un pedido incluyendo todas sus líneas de detalle (Eager Loading)."""
        pass

    @abstractmethod
    async def update_order_status(self, order_id: uuid.UUID, new_status: OrderStatus) -> Order:
        """Actualiza el estado de un pedido."""
        pass

    @abstractmethod
    async def get_business_orders(self, business_id: uuid.UUID, status_filter: OrderStatus | None = None) -> Sequence[Order]:
        """Obtiene el listado de pedidos de un negocio, filtrable por estado."""
        pass

    @abstractmethod
    async def get_user_orders(self, user_id: uuid.UUID) -> Sequence[Order]:
        """Obtiene el historial de compras de un usuario."""
        pass
    
    

class IStaffService(ABC):
    
    @abstractmethod
    async def add_staff_member( self, business_id: uuid.UUID, name: str, specialty: str | None = None) -> Staff:
        pass
    
    @abstractmethod
    async def get_business_staff(self, business_id: uuid.UUID) -> Sequence[Staff] | None:
        pass
    
    @abstractmethod
    async def toggle_staff_status(self, staff_id: uuid.UUID) -> Staff:
        pass
    

class ISubscriptionService(ABC):
    """
    Contrato para el servicio de Suscripciones.
    Define las operaciones exclusivas de base de datos para membresías y pagos recurrentes.
    """
    
    @abstractmethod
    async def create_full_subscription(self, new_subscription: Subscription, items: list[SubscriptionItem]) -> Subscription:
        """Guarda la cabecera de la suscripción y sus detalles atómicamente."""
        pass

    @abstractmethod
    async def get_subscription_with_items(self, subscription_id: uuid.UUID) -> Subscription | None:
        """Obtiene una suscripción incluyendo sus planes/items."""
        pass

    @abstractmethod
    async def update_status(self, subscription_id: uuid.UUID, new_status: str, period_end: datetime | None = None) -> Subscription:
        """Actualiza el estado de la suscripción (ej. active, canceled, past_due)."""
        pass

    @abstractmethod
    async def record_payment(self, payment_data: dict) -> SubscriptionPayment:
        """Registra un cobro exitoso o fallido en el historial de la suscripción."""
        pass

    @abstractmethod
    async def get_user_subscriptions(self, user_id: uuid.UUID) -> Sequence[Subscription]:
        """Obtiene todas las suscripciones de un usuario."""
        pass

    @abstractmethod
    async def get_business_subscriptions(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[Subscription]:
        """Obtiene las suscripciones de un negocio (útil para reportes)."""
        pass
    
    

class IReviewService(ABC):
    """Contrato para gestionar los 3 tipos de reseñas del sistema."""
    
    @abstractmethod
    async def create_order_review(self, review: OrderReview) -> OrderReview:
        pass

    @abstractmethod
    async def get_business_reviews(self, business_id: uuid.UUID) -> Sequence[OrderReview]:
        pass

    @abstractmethod
    async def create_item_review(self, review: ItemReview) -> ItemReview:
        pass

    @abstractmethod
    async def get_item_reviews(self, item_id: uuid.UUID) -> Sequence[ItemReview]:
        pass

    @abstractmethod
    async def create_staff_review(self, review: StaffReview) -> StaffReview:
        pass

    @abstractmethod
    async def get_staff_reviews(self, staff_id: uuid.UUID) -> Sequence[StaffReview]:
        pass
    

class IKnowledgeService(ABC):
    """
    Contrato para el servicio de Base de Conocimiento (IA).
    Define las operaciones específicas para gestionar los documentos que alimentan al RAG.
    """
    
    @abstractmethod
    async def get_business_sources(self, business_id: uuid.UUID, active_only: bool = True) -> Sequence[KnowledgeSource]:
        """Obtiene la lista de documentos y enlaces asociados a un negocio."""
        pass

    @abstractmethod
    async def mark_as_indexed(self, source_id: uuid.UUID) -> KnowledgeSource:
        """Actualiza la fecha de última indexación (last_indexed_at) cuando la IA procesa el documento."""
        pass