from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

from dto.user import UserCreate
from services import UserService

router = APIRouter()


class UserModel(BaseModel):
    login: str
    name: str
    password: str


@router.post("/register")
async def register_user(user: UserModel):
    does_user_exist = await UserService.does_exist_by_login(login=user.login)
    if does_user_exist:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await UserService.create(UserCreate(login=user.login, name=user.name, password=user.password))
