import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

# Commands y Queries
from app.application.command.Catalog import CatalogCommands
from app.application.query.Catalog import CatalogQueries

# Schemas
from app.domain.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)

# Dependencia de la base de datos
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# RUTAS DE CATEGORÍAS
# ==========================================

@router.get("/categories/business/{business_id}", response_model=list[CategoryRead], status_code=status.HTTP_200_OK)
async def get_categories_by_business(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Lista todas las categorías de un negocio (el menú principal)."""
    queries = CatalogQueries(db)
    return await queries.get_categories_by_business(business_id)

@router.get("/categories/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK)
async def get_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene los detalles de una categoría específica."""
    queries = CatalogQueries(db)
    return await queries.get_category(category_id)

@router.post("/categories/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_session)):
    """Crea una nueva categoría para un negocio."""
    commands = CatalogCommands(db)
    return await commands.create_category(category_in)

@router.patch("/categories/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK)
async def update_category(category_id: uuid.UUID, category_in: CategoryUpdate, db: AsyncSession = Depends(get_session)):
    """Actualiza el nombre o descripción de una categoría."""
    commands = CatalogCommands(db)
    return await commands.update_category(category_id, category_in)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina una categoría (soft delete)."""
    commands = CatalogCommands(db)
    await commands.delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# RUTAS DE ÍTEMS (PRODUCTOS / SERVICIOS)
# ==========================================

@router.get("/items/business/{business_id}", response_model=list[ItemRead], status_code=status.HTTP_200_OK)
async def get_items_by_business(business_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Lista el catálogo completo de productos/servicios de un negocio."""
    queries = CatalogQueries(db)
    return await queries.get_items_by_business(business_id)

@router.get("/items/category/{category_id}", response_model=list[ItemRead], status_code=status.HTTP_200_OK)
async def get_items_by_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Filtra los productos/servicios que pertenecen a una categoría."""
    queries = CatalogQueries(db)
    return await queries.get_items_by_category(category_id)

@router.get("/items/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene el detalle de un producto o servicio."""
    queries = CatalogQueries(db)
    return await queries.get_item(item_id)

@router.post("/items/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate, db: AsyncSession = Depends(get_session)):
    """Registra un nuevo producto o servicio en el catálogo."""
    commands = CatalogCommands(db)
    return await commands.create_item(item_in)

@router.patch("/items/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
async def update_item(item_id: uuid.UUID, item_in: ItemUpdate, db: AsyncSession = Depends(get_session)):
    """Actualiza la información (precio, nombre, etc.) de un producto o servicio."""
    commands = CatalogCommands(db)
    return await commands.update_item(item_id, item_in)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina un producto o servicio (soft delete)."""
    commands = CatalogCommands(db)
    await commands.delete_item(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)