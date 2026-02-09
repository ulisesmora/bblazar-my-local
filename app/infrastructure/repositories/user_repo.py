from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.domain.models.models import SocialProvider, User, UserRole
from app.domain.repositories.repositories import IUserRepository
from app.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_phone(self, phone: str) -> User | None:
        statement = select(User).where(User.phone == phone)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_social_id(self, provider: SocialProvider, social_id: str) -> User | None:
        """
        Busca un usuario por su identificador social de forma segura.
        Utiliza scalar_one_or_none para evitar excepciones si el usuario no existe.
        """
        column_name = f"{provider.value}_id"
        column = getattr(User, column_name)
        statement = select(User).where(column == social_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create_social_user(
        self, 
        provider: SocialProvider, 
        social_id: str, 
        email: str | None = None, 
        full_name: str | None = None,
        phone: str | None = None,
        image_url: str | None = None
    ) -> User:
        """
        Crea un usuario desde un login social.
        Se utiliza setattr para asignar el ID social dinámico, evitando que Pylance
        reporte errores de asignación de tipos en el constructor de User.
        """
        # Creamos la instancia con los campos fijos para que Pylance valide los tipos correctamente
        user = User(
            email=email,
            full_name=full_name,
            image_url=image_url,
            role=UserRole.CLIENT,
            phone=phone
        )
        
        # Asignamos el campo dinámico (google_id, apple_id, etc.) fuera del constructor
        setattr(user, f"{provider.value}_id", social_id)
        
        return await self.create(user)