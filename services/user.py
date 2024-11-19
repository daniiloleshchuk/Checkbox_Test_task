from typing import Optional

from dto import User, UserCreate
from repositories import UserRepository
from services.auth import AuthService


class UserService:
    @classmethod
    async def does_exist_by_login(cls, login: str) -> bool:
        return bool(await UserRepository.get_by_login(login=login))

    @classmethod
    async def authenticate(cls, login: str, password: str) -> bool:
        user = await UserRepository.get_by_login(login=login)
        if not user:
            return False
        if not AuthService.verify_password(password, user["hashed_password"]):
            return False
        return True

    @classmethod
    async def create(cls, user: UserCreate) -> User:
        return await UserRepository.save(user)

    @classmethod
    async def get_by_login(cls, login: str) -> Optional[User]:
        return await UserRepository.get_by_login(login=login)

    @classmethod
    async def get_id_by_login(cls, login: str) -> Optional[int]:
        return await UserRepository.get_id_by_login(login)
