from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.core.config import get_settings
from backend.schemas.auth import TokenData
from backend.crud.user import get_user

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        raise credentials_exception

    user = get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user
