from typing import Optional

from sqlalchemy.orm import Session

from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate, role: str = "tester") -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
