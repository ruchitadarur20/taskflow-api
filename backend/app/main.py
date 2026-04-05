from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.comments import router as comments_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router
from app.api.websocket import router as ws_router
from app.core.limiter import limiter
from app.db.database import engine

app = FastAPI(
    title="TaskFlow API",
    description="A task and project management API with real-time notifications.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(ws_router)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://taskflow-1o0cll5tv-ruchita-darurs-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)