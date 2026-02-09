import uuid
from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from sqlalchemy import JSON, Column, Index, Numeric, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

# --- CLASE BASE PARA TRAZABILIDAD Y SOFT DELETE ---



class TimestampModel(SQLModel):
    """
    Clase base para añadir auditoría y borrado lógico (soft delete).
    Mantiene registro de creación, última actualización y fecha de eliminación.
    """
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False
    )
    deleted_at: datetime | None = Field(default=None, index=True)

# --- ENUMERACIONES (StrEnum para compatibilidad moderna) ---


class SocialProvider(StrEnum):
    """Proveedores de identidad soportados por el sistema."""
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    LOCAL = "local"


class UserRole(StrEnum):
    BUSINESS_OWNER = "owner"
    STAFF = "staff"
    CLIENT = "client"
    GUEST = "guest"

class ItemType(StrEnum):
    PRODUCT = "product"
    SERVICE = "service"

class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COLLECTED = "collected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"

class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class SubscriptionStatus(StrEnum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"

class KnowledgeSourceType(StrEnum):
    FILE = "file"
    TEXT = "text"
    WEBSITE = "website"

# --- IDENTIDAD Y USUARIOS ---

class User(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    phone: str | None = Field(unique=True, index=True)
    email: str | None = Field(default=None, unique=True)
    full_name: str | None = None
    hashed_password: str | None = None
    role: UserRole = Field(default=UserRole.GUEST)
    trust_score: int = Field(default=100)
    image_url: str | None = None
    
    # Relaciones
    owned_businesses: list["Business"] = Relationship(back_populates="owner")
    wallets: list["Wallet"] = Relationship(back_populates="user")
    orders: list["Order"] = Relationship(back_populates="user")
    subscriptions: list["Subscription"] = Relationship(back_populates="user")
    reviews_given: list["OrderReview"] = Relationship(back_populates="user")
    staff_profile: Optional["Staff"] = Relationship(back_populates="user")

# --- NEGOCIO, PERSONAL Y CONFIGURACIÓN DE IA (MCP) ---

class Business(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    name: str
    slug: str = Field(unique=True, index=True)
    stripe_account_id: str | None = None
    
    # Personalización visual de marca
    image_url: str | None = None
    primary_color: str = Field(default="#4A90E2")
    secondary_color: str = Field(default="#F5A623")
    
    # Configuración para el Model Context Protocol (MCP)
    ai_enabled: bool = Field(default=True)
    ai_assistant_name: str = Field(default="Asistente Virtual")
    ai_system_prompt: str | None = Field(default=None, sa_column=Column(Text))
    
    settings: dict | None = Field(default_factory=dict, sa_column=Column(JSON))
    
    wallets: list["Wallet"] = Relationship(back_populates="business")
    # Relaciones
    owner: User = Relationship(back_populates="owned_businesses")
    categories: list["Category"] = Relationship(back_populates="business")
    items: list["Item"] = Relationship(back_populates="business")
    recharge_plans: list["RechargePlan"] = Relationship(back_populates="business")
    subscriptions: list["Subscription"] = Relationship(back_populates="business")
    operating_hours: list["BusinessHour"] = Relationship(back_populates="business")
    reviews: list["OrderReview"] = Relationship(back_populates="business")
    staff: list["Staff"] = Relationship(back_populates="business")
    knowledge_base: list["KnowledgeSource"] = Relationship(back_populates="business")

class Staff(TimestampModel, table=True):
    """Personal humanizado con bio y redes sociales."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    name: str
    specialty: str | None = None
    
    bio: str | None = Field(default=None, sa_column=Column(Text))
    image_url: str | None = None
    social_links: dict | None = Field(default_factory=dict, sa_column=Column(JSON))
    rating_avg: Decimal = Field(default=0.0, sa_column=Column(Numeric(precision=3, scale=2)))
    is_active: bool = Field(default=True)
    
    business: Business = Relationship(back_populates="staff")
    user: User | None = Relationship(back_populates="staff_profile")
    items_handled: list["OrderItem"] = Relationship(back_populates="assigned_staff")
    reviews: list["StaffReview"] = Relationship(back_populates="staff")

class KnowledgeSource(TimestampModel, table=True):
    """Información para alimentar el RAG del Bot MCP."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    title: str
    content: str | None = Field(default=None, sa_column=Column(Text))
    source_url: str | None = None
    source_type: KnowledgeSourceType = Field(default=KnowledgeSourceType.TEXT)
    last_indexed_at: datetime | None = None
    is_active: bool = Field(default=True)
    
    business: Business = Relationship(back_populates="knowledge_base")

class BusinessHour(TimestampModel, table=True):
    """Gestión de horarios y capacidad operativa por slot."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    day_of_week: int 
    open_time: time
    close_time: time
    slot_capacity: int = Field(default=5)
    
    business: Business = Relationship(back_populates="operating_hours")

# --- CATÁLOGO e INVENTARIO ---

class Category(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    name: str
    description: str | None = None
    
    business: Business = Relationship(back_populates="categories")
    items: list["Item"] = Relationship(back_populates="category")

class Item(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    category_id: uuid.UUID = Field(foreign_key="category.id")
    name: str
    description: str | None = Field(default=None, sa_column=Column(Text))
    image_url: str | None = None
    price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    type: ItemType = Field(default=ItemType.PRODUCT)
    is_subscription_eligible: bool = Field(default=False)
    stripe_price_id: str | None = None
    
    business: Business = Relationship(back_populates="items")
    category: Category = Relationship(back_populates="items")
    subscription_items: list["SubscriptionItem"] = Relationship(back_populates="item")
    daily_stocks: list["DailyInventory"] = Relationship(back_populates="item")
    reviews: list["ItemReview"] = Relationship(back_populates="item")

class DailyInventory(TimestampModel, table=True):
    """Control de stock diario para evitar sobreventas."""
    __table_args__ = (UniqueConstraint("item_id", "date", name="unique_item_stock_per_day"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    item_id: uuid.UUID = Field(foreign_key="item.id")
    date: date
    quantity_produced: int
    quantity_available: int
    
    item: Item = Relationship(back_populates="daily_stocks")

# --- FINANZAS Y MONEDERO ---

class RechargePlan(TimestampModel, table=True):
    """Planes de fidelización: Recarga X, recibe Y."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    credit: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    is_active: bool = Field(default=True)
    
    business: Business = Relationship(back_populates="recharge_plans")

class Wallet(TimestampModel, table=True):
    """Saldo prepago por usuario y negocio."""
    __table_args__ = (UniqueConstraint("user_id", "business_id", name="unique_wallet_per_business"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    business_id: uuid.UUID = Field(foreign_key="business.id")
    balance: Decimal = Field(default=0.0, sa_column=Column(Numeric(precision=10, scale=2)))
    
    user: User = Relationship(back_populates="wallets")
    business: Business = Relationship(back_populates="wallets")
    transactions: list["WalletTransaction"] = Relationship(back_populates="wallet")

class WalletTransaction(TimestampModel, table=True):
    """Libro mayor inmutable para auditoría financiera."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    wallet_id: uuid.UUID = Field(foreign_key="wallet.id")
    amount: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    type: TransactionType
    description: str
    reference_id: uuid.UUID | None = Field(default=None, index=True)
    external_reference: str | None = Field(default=None)
    
    wallet: Wallet = Relationship(back_populates="transactions")

# --- SUSCRIPCIONES Y PAGOS RECURRENTES ---

class Subscription(TimestampModel, table=True):
    """Motor de recurrencia integrado con Stripe Billing."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    business_id: uuid.UUID = Field(foreign_key="business.id")
    stripe_subscription_id: str | None = Field(default=None, index=True)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.INCOMPLETE)
    current_period_end: datetime | None = None
    frequency_days: str # ej: "MON,WED,FRI"
    pickup_time: time
    is_active: bool = Field(default=True)
    last_generated_date: date | None = None
    
    user: User = Relationship(back_populates="subscriptions")
    business: Business = Relationship(back_populates="subscriptions")
    items: list["SubscriptionItem"] = Relationship(back_populates="subscription")
    payments: list["SubscriptionPayment"] = Relationship(back_populates="subscription")

class SubscriptionItem(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="subscription.id")
    item_id: uuid.UUID = Field(foreign_key="item.id")
    quantity: int = Field(default=1)
    
    subscription: Subscription = Relationship(back_populates="items")
    item: Item = Relationship(back_populates="subscription_items")

class SubscriptionPayment(TimestampModel, table=True):
    """Registro de cada invoice cobrado por Stripe."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="subscription.id")
    stripe_invoice_id: str = Field(index=True)
    amount: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    status: str 
    
    subscription: Subscription = Relationship(back_populates="payments")

# --- PEDIDOS Y DETALLES ---

class Order(TimestampModel, table=True):
    """Cabecera de pedido (manual o por suscripción)."""
    __table_args__ = (Index("ix_order_business_status", "business_id", "status"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    subscription_id: uuid.UUID | None = Field(default=None, foreign_key="subscription.id")
    is_subscription_order: bool = Field(default=False)
    pickup_slot: datetime
    
    user: User = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")
    review: Optional["OrderReview"] = Relationship(back_populates="order")

class OrderItem(TimestampModel, table=True):
    """Línea de detalle con asignación de personal para servicios."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="order.id")
    item_id: uuid.UUID = Field(foreign_key="item.id")
    staff_id: uuid.UUID | None = Field(default=None, foreign_key="staff.id")
    quantity: int
    unit_price: Decimal = Field(sa_column=Column(Numeric(precision=10, scale=2)))
    
    order: Order = Relationship(back_populates="items")
    assigned_staff: Optional["Staff"] = Relationship(back_populates="items_handled")

# --- SISTEMA DE RESEÑAS DETALLADAS ---

class OrderReview(TimestampModel, table=True):
    """Reseña logística del pedido y local."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    order_id: uuid.UUID = Field(foreign_key="order.id", unique=True)
    
    rating_attention: int = Field(ge=1, le=5)
    rating_speed: int = Field(ge=1, le=5)
    rating_location: int = Field(ge=1, le=5)
    rating_general: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, sa_column=Column(Text))
    
    user: User = Relationship(back_populates="reviews_given")
    business: Business = Relationship(back_populates="reviews")
    order: Order = Relationship(back_populates="review")

class ItemReview(TimestampModel, table=True):
    """Reseña de calidad de un producto o servicio específico."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    item_id: uuid.UUID = Field(foreign_key="item.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    order_id: uuid.UUID = Field(foreign_key="order.id")
    
    rating_quality: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, sa_column=Column(Text))
    
    item: Item = Relationship(back_populates="reviews")

class StaffReview(TimestampModel, table=True):
    """Reseña del trato recibido por un miembro del staff."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    staff_id: uuid.UUID = Field(foreign_key="staff.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    order_id: uuid.UUID = Field(foreign_key="order.id")
    
    rating_service: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, sa_column=Column(Text))
    
    staff: Staff = Relationship(back_populates="reviews")
    
