from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from schemas.user import UserCreate
from settings.db import get_db
from utils.security import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email),
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id),
        )
        return result.scalars().first()

    async def create(self, data: UserCreate) -> User:
        hashed_password = get_password_hash(data.password)
        new_user = User(
            email=data.email,
            name=data.name,
            hashed_password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)
