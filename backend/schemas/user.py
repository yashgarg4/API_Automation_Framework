from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode
