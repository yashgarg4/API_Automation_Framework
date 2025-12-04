from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.deps import get_db
from backend.core.config import get_settings
from backend.core.security import verify_password, create_access_token
from backend.crud.user import get_user_by_email, create_user
from backend.schemas.user import UserCreate, UserOut
from backend.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


@router.post("/register", response_model=UserOut)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = create_user(db, user_in=user_in, role="tester")
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Standard OAuth2 password flow.
    Expects: username (email), password
    """
    user = get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)
