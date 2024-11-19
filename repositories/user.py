from typing import Optional

from sqlalchemy import select

from database import get_session, User as UserDBModel
from dto import User, UserCreate
from services import AuthService


class UserRepository:
    @classmethod
    async def save(cls, user: UserCreate) -> User:
        hashed_password = AuthService.hash_password(user["password"])
        entity = UserDBModel(
            name=user["name"],
            login=user["login"],
            hashed_password=hashed_password,
        )
        async with get_session() as session:
            session.add(entity)
            await session.commit()
        return User(
            login=user["login"],
            name=user["name"],
            hashed_password=hashed_password,
        )

    @classmethod
    async def get_by_login(cls, login: str) -> Optional[User]:
        async with get_session() as session:
            data = (await session.execute(
                select(UserDBModel).where(UserDBModel.login == login)
            )).scalars().first()
        if data:
            return User(
                login=data.login,
                name=data.name,
                hashed_password=data.hashed_password,
            )

    @classmethod
    async def get_id_by_login(cls, login: str) -> Optional[int]:
        async with get_session() as session:
            user_id = (await session.execute(
                select(UserDBModel.id).where(UserDBModel.login == login)
            )).scalars().first()
        return user_id

