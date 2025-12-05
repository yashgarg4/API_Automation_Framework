from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TestRunBase(BaseModel):
    run_type: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    summary: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None


class TestRun(TestRunBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2
