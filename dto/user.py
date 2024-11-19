from typing import TypedDict


class User(TypedDict):
    name: str
    login: str
    hashed_password: str


class UserCreate(TypedDict):
    name: str
    login: str
    password: str
