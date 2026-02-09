import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from app.domain.models.models import (
    Business,
    SocialProvider,
    User,
    Wallet,
    WalletTransaction,
)

ModelType = TypeVar("ModelType")

class IBaseRepository(ABC, Generic[ModelType]):
    """
    Contrato base para cualquier operación de persistencia.
    Ubicación: app/domain/interfaces/
    """
    @abstractmethod
    async def list_all(self) -> Sequence[ModelType] | None:
        pass
    
    @abstractmethod
    async def get(self, id: uuid.UUID) -> ModelType | None:
        pass

    @abstractmethod
    async def create(self, obj_in: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def update(
        self, db_obj: ModelType, obj_in: ModelType | dict[str, Any]
    ) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        pass

class IUserRepository(IBaseRepository[User]):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_social_id(self, provider: SocialProvider, social_id: str) -> User | None:
        pass

    @abstractmethod
    async def create_social_user(
        self, provider: SocialProvider, social_id: str, email: str, full_name: str,phone: str, image_url: str
    ) -> User:
        pass

class IBusinessRepository(IBaseRepository[Business]):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Business | None:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: uuid.UUID) -> Sequence[Business]:
        pass

    @abstractmethod
    async def check_slug_availability(self, slug: str) -> bool:
        pass

class IWalletRepository(IBaseRepository[Wallet]):
    @abstractmethod
    async def get_by_user_and_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Wallet | None:
        pass

    @abstractmethod
    async def get_transactions(self, wallet_id: uuid.UUID, limit: int = 20) -> Sequence[WalletTransaction]:
        pass

    @abstractmethod
    async def add_transaction(self, transaction: WalletTransaction) -> WalletTransaction:
        pass