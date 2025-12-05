from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

from backend.db.session import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_type = Column(String, index=True)  # e.g. "ai_executor", "api", "ui"
    status = Column(String, index=True)    # "running", "passed", "failed", "error"

    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    summary = Column(JSON, nullable=True)  # high-level summary dict
    results = Column(JSON, nullable=True)  # list of per-test results
