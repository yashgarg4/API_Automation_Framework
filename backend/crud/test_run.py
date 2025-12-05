from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.test_run import TestRun


def create_test_run(
    db: Session,
    run_type: str,
    status: str = "running",
) -> TestRun:
    obj = TestRun(
        run_type=run_type,
        status=status,
        started_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def finish_test_run(
    db: Session,
    test_run: TestRun,
    status: str,
    summary: dict | None = None,
    results: list | None = None,
) -> TestRun:
    test_run.status = status
    test_run.summary = summary
    test_run.results = results
    test_run.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(test_run)
    return test_run


def list_test_runs(
    db: Session,
    run_type: Optional[str] = None,
    limit: int = 20,
) -> List[TestRun]:
    q = db.query(TestRun).order_by(TestRun.started_at.desc())
    if run_type:
        q = q.filter(TestRun.run_type == run_type)
    return q.limit(limit).all()
