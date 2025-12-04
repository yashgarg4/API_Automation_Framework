from datetime import datetime
from typing import Literal

from pydantic import BaseModel


SeverityType = Literal["low", "medium", "high", "critical"]
PriorityType = Literal["low", "medium", "high"]
StatusType = Literal["open", "in_progress", "resolved", "closed"]


class BugBase(BaseModel):
    title: str
    description: str | None = None
    severity: SeverityType = "medium"
    priority: PriorityType = "medium"


class BugCreate(BugBase):
    # project_id will come from path param
    assignee_id: int | None = None


class BugUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: SeverityType | None = None
    priority: PriorityType | None = None
    assignee_id: int | None = None


class BugStatusUpdate(BaseModel):
    status: StatusType


class BugOut(BugBase):
    id: int
    status: StatusType
    project_id: int
    reporter_id: int
    assignee_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
