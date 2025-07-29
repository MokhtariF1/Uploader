
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import engine, Base
from .routers import auth, files
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown: no-op

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(files.router, prefix=settings.API_PREFIX + "/files")
