from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_active_user
from backend.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from backend.crud import project as project_crud
from backend.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    projects = project_crud.get_projects_for_user(db, user_id=current_user.id)
    return projects


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return project_crud.create_project(db, project_in, owner=current_user)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_project = project_crud.get_project(db, project_id)
    if not db_project or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return db_project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_project = project_crud.get_project(db, project_id)
    if not db_project or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project_crud.update_project(db, db_project, project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_project = project_crud.get_project(db, project_id)
    if not db_project or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project_crud.delete_project(db, db_project)
    return None
