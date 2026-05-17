from fastapi import FastAPI
from routers import meals

app = FastAPI(title="Meal Recipe Explorer")
app.include_router(meals.router)
