from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, user_data)

    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, user_data)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return token