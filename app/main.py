from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)


@app.get("/")
def root():
    return {"message": "TaskFlow API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def test_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}