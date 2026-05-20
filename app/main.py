from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="Project",
    description="CRUD додаток для користувачів з валідацією Pydantic",
    version="1.0.0"
)

# Підключаємо наш новий ізольований роутер з папки routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI CRUD! Go to /docs for Swagger UI."}