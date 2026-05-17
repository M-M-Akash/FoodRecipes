from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.logging import setup_logging
from routers import meals


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(title="Meal Recipe Explorer", lifespan=lifespan)
app.include_router(meals.router)
