from typing import List, Optional

from sqlalchemy.orm import Session

from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectUpdate
from backend.models.user import User


def create_project(
    db: Session,
    project_in: ProjectCreate,
    owner: User,
) -> Project:
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=owner.id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def get_projects_for_user(db: Session, user_id: int) -> List[Project]:
    return (
        db.query(Project)
        .filter(Project.owner_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def update_project(
    db: Session,
    db_project: Project,
    project_in: ProjectUpdate,
) -> Project:
    if project_in.name is not None:
        db_project.name = project_in.name
    if project_in.description is not None:
        db_project.description = project_in.description

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, db_project: Project) -> None:
    db.delete(db_project)
    db.commit()
