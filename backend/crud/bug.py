from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.bug import Bug
from backend.schemas.bug import BugCreate, BugUpdate
from backend.models.user import User


ALLOWED_STATUS_TRANSITIONS = {
    "open": {"in_progress", "resolved"},
    "in_progress": {"resolved"},
    "resolved": {"closed", "in_progress"},
    "closed": set(),  # no transitions allowed from closed
}


def validate_status_transition(old_status: str, new_status: str) -> bool:
    allowed = ALLOWED_STATUS_TRANSITIONS.get(old_status, set())
    return new_status in allowed


def create_bug(
    db: Session,
    project_id: int,
    bug_in: BugCreate,
    reporter: User,
) -> Bug:
    db_bug = Bug(
        title=bug_in.title,
        description=bug_in.description,
        severity=bug_in.severity,
        priority=bug_in.priority,
        status="open",
        project_id=project_id,
        reporter_id=reporter.id,
        assignee_id=bug_in.assignee_id,
    )
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    return db_bug


def get_bug(db: Session, bug_id: int) -> Optional[Bug]:
    return db.query(Bug).filter(Bug.id == bug_id).first()


def get_bugs_for_project(
    db: Session,
    project_id: int,
) -> List[Bug]:
    return (
        db.query(Bug)
        .filter(Bug.project_id == project_id)
        .order_by(Bug.created_at.desc())
        .all()
    )


def update_bug(
    db: Session,
    db_bug: Bug,
    bug_in: BugUpdate,
) -> Bug:
    if bug_in.title is not None:
        db_bug.title = bug_in.title
    if bug_in.description is not None:
        db_bug.description = bug_in.description
    if bug_in.severity is not None:
        db_bug.severity = bug_in.severity
    if bug_in.priority is not None:
        db_bug.priority = bug_in.priority
    if bug_in.assignee_id is not None:
        db_bug.assignee_id = bug_in.assignee_id

    db.commit()
    db.refresh(db_bug)
    return db_bug


def update_bug_status(
    db: Session,
    db_bug: Bug,
    new_status: str,
) -> Bug:
    if not validate_status_transition(db_bug.status, new_status):
        raise ValueError(f"Invalid status transition from {db_bug.status} to {new_status}")

    db_bug.status = new_status
    db.commit()
    db.refresh(db_bug)
    return db_bug
