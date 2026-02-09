import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any, Generic, TypeVar

from app.domain.models.models import (
    Business,
    Category,
    DailyInventory,
    Item,
    Order,
    Staff,
    Wallet,
)
from app.domain.schemas.auth import LoginRequest, SocialLoginRequest, Token
from app.domain.schemas.business import BusinessCreate
from app.domain.schemas.category import CategoryCreate, ItemCreate
from app.domain.schemas.orders import OrderCreate

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
    Contrato para el procesamiento de órdenes.
    Es el servicio más complejo ya que orquesta Wallet, Inventory y Catalog.
    """
    @abstractmethod
    async def create_order(self, user_id: uuid.UUID, data: OrderCreate) -> Order:
        """Coordina el cobro en Wallet, descuento de stock y registro del pedido."""
        pass

    @abstractmethod
    async def get_user_orders(self, user_id: uuid.UUID) -> Sequence[Order]:
        """Obtiene el historial de compras del usuario."""
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