from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine


app = FastAPI(title="TaskFlow API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)


@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def test_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}

@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def test_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}