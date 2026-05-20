from fastapi import FastAPI
from app.routers import users, products, auth  # Перевірь, чи є тут auth

app = FastAPI(
    title="Project",
    description="CRUD додаток для користувачів з JWT та Cookies",
    version="1.0.0"
)

# Підключаємо всі роутери
app.include_router(auth.router)  # <--- КРИТИЧНО: Перевірь цей рядок
app.include_router(users.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI CRUD! Go to /docs for Swagger UI."}