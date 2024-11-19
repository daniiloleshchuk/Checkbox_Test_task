import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = os.environ.get("SECRET_KEY", "SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM", "ALGORITHM")


class AuthService:
    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode["exp"] = expire
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @classmethod
    def authenticate(cls, token: str = Depends(oauth2_scheme)) -> dict:
        error_403 = HTTPException(status_code=403, detail="Token is invalid or expired")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            login: str = payload.get("login")
            if login is None:
                raise error_403
            return payload
        except jwt.exceptions.PyJWTError:
            raise error_403
