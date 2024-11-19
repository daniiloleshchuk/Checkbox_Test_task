from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from services import AuthService, UserService

ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter()


@router.post("/token")
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    authenticated = await UserService.authenticate(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"login": form_data.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token}


@router.get("/verify-token/")
async def verify_token(token: str):
    if AuthService.authenticate(token):
        return {"message": "Token is valid"}
