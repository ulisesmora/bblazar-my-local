import uuid
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

# Commands y Queries
from app.application.command.Inventory import InventoryCommands
from app.application.query.Inventory import InventoryQueries

# Schemas
from app.domain.schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate

# Dependencia de la base de datos
from app.infrastructure.database.database import get_session

router = APIRouter()

# ==========================================
# QUERIES (Lecturas - GET)
# ==========================================

@router.get("/history/{item_id}", response_model=list[InventoryRead], status_code=status.HTTP_200_OK)
async def get_item_history(item_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene todo el historial de inventario de un producto (del más reciente al más antiguo)."""
    queries = InventoryQueries(db)
    return await queries.get_item_history(item_id)

@router.get("/stock/{item_id}/{target_date}", response_model=InventoryRead, status_code=status.HTTP_200_OK)
async def get_stock_for_date(item_id: uuid.UUID, target_date: date, db: AsyncSession = Depends(get_session)):
    """Obtiene el registro exacto de stock de un producto para una fecha en particular."""
    queries = InventoryQueries(db)
    return await queries.get_stock_for_date(item_id, target_date)

@router.get("/availability", status_code=status.HTTP_200_OK)
async def check_availability(
    item_id: uuid.UUID = Query(...), 
    target_date: date = Query(...), 
    requested_qty: int = Query(...) ,
    db: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    """
    Verifica si hay stock suficiente para cubrir una venta.
    (Ideal para validaciones de carrito de compras).
    """
    queries = InventoryQueries(db)
    return await queries.check_item_availability(item_id, target_date, requested_qty)

@router.get("/{inventory_id}", response_model=InventoryRead, status_code=status.HTTP_200_OK)
async def get_inventory_record(inventory_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Obtiene un registro específico de inventario por su ID interno."""
    queries = InventoryQueries(db)
    return await queries.get_inventory_record(inventory_id)


# ==========================================
# COMMANDS (Escrituras - POST, PUT, PATCH, DELETE)
# ==========================================

@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def register_initial_stock(inventory_in: InventoryCreate, db: AsyncSession = Depends(get_session)):
    """
    Registra el stock inicial del día para un producto. 
    Lanza error 400 si ya existe un registro en esa fecha.
    """
    commands = InventoryCommands(db)
    return await commands.register_daily_stock(inventory_in)

@router.put("/set-stock", response_model=InventoryRead, status_code=status.HTTP_200_OK)
async def set_daily_stock(
    item_id: uuid.UUID = Query(...), 
    target_date: date = Query(...), 
    quantity: int = Query(...),
    db: AsyncSession = Depends(get_session)
):
    """
    Establece el stock de forma segura (Upsert). 
    Si no existe lo crea, si existe lo actualiza.
    """
    commands = InventoryCommands(db)
    return await commands.set_stock(item_id, target_date, quantity)

@router.patch("/{inventory_id}", response_model=InventoryRead, status_code=status.HTTP_200_OK)
async def update_inventory(
    inventory_id: uuid.UUID, 
    inventory_in: InventoryUpdate, 
    db: AsyncSession = Depends(get_session)
):
    """Ajuste manual y parcial del inventario (ej. registrar mermas o aumentar disponibilidad)."""
    commands = InventoryCommands(db)
    return await commands.update_daily_stock(inventory_id, inventory_in)

@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    """Elimina un registro de inventario (soft delete)."""
    commands = InventoryCommands(db)
    await commands.delete_daily_stock(inventory_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)