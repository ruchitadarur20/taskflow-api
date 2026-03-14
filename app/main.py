from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine

app = FastAPI()


@app.get("/")
def root():
    return {"message": "TaskFlow API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def test_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
    return {"database": "connected"}