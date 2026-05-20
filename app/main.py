from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Template",
    description="Базовий шаблон",
    version="1.0.0")

@app.get("/")
def root():
    return {"status": "working", "message": "Hello World from FastAPI Template"}