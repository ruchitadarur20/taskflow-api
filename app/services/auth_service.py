from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, user_data: UserRegister):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return None

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        role_id=1
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(db: Session, user_data: UserLogin):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        return None

    if not verify_password(user_data.password, user.hashed_password):
        return None

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }