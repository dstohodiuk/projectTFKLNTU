from fastapi import FastAPI
from app.routers import users, products

app = FastAPI(
    title="Project",
    description="CRUD додаток для користувачів",
    version="1.0.0"
)

# Підключаємо наші роутери до додатка
app.include_router(users.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI CRUD! Go to /docs for Swagger UI."}
