import uuid
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.command.Users import UserCommands
from app.application.query.Users import UserQueries
from app.domain.schemas.users import UserCreate, UserRead
from app.infrastructure.database.database import get_session

# 1. AQUÍ NACE: Definimos la variable 'router' que luego importaremos
router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate, 
    db: AsyncSession = Depends(get_session)
) -> Any:
    command = UserCommands(db)
    return await command.register_user(data)

@router.get("/", response_model=Sequence[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_session)
) -> Any:
    query = UserQueries(db)
    return await query.list_active_users()

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID, 
    db: AsyncSession = Depends(get_session)
) -> Any:
    query = UserQueries(db)
    user = await query.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user