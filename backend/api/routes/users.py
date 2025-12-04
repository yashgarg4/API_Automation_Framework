from fastapi import APIRouter, Depends

from backend.api.deps import get_current_active_user
from backend.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user
