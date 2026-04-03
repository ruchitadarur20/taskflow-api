from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
@limiter.limit("10/minute")
def register(
    request: Request,
    full_name: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        role_id=1,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    db.add(RefreshToken(
        token=refresh_token,
        user_id=user.id,
        is_revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    ))
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        decoded = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == payload.refresh_token,
        RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or revoked token")

    return {"access_token": create_access_token(data={"sub": email}), "token_type": "bearer"}


@router.post("/logout")
def logout(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == payload.refresh_token,
        RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or already revoked token")

    db_token.is_revoked = True
    db.commit()
    return {"message": "Logged out successfully"}
