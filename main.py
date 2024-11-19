from fastapi import FastAPI

from database import init_db
from routes import users_router, auth_router, receipt_router

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(receipt_router, prefix="/receipt")


@app.on_event("startup")
async def on_startup():
    await init_db()
