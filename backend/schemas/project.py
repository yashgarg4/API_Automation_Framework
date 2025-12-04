from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectOut(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
