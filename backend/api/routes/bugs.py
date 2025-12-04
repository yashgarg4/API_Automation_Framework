from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_active_user
from backend.crud import project as project_crud
from backend.crud import bug as bug_crud
from backend.schemas.bug import BugCreate, BugOut, BugUpdate, BugStatusUpdate
from backend.models.user import User

router = APIRouter(tags=["bugs"])


@router.get("/projects/{project_id}/bugs", response_model=List[BugOut])
def list_bugs_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    project = project_crud.get_project(db, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    bugs = bug_crud.get_bugs_for_project(db, project_id=project_id)
    return bugs


@router.post(
    "/projects/{project_id}/bugs",
    response_model=BugOut,
    status_code=status.HTTP_201_CREATED,
)
def create_bug_for_project(
    project_id: int,
    bug_in: BugCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    project = project_crud.get_project(db, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    bug = bug_crud.create_bug(
        db,
        project_id=project_id,
        bug_in=bug_in,
        reporter=current_user,
    )
    return bug


@router.get("/bugs/{bug_id}", response_model=BugOut)
def get_bug(
    bug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_bug = bug_crud.get_bug(db, bug_id)
    if not db_bug or db_bug.project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bug not found")
    return db_bug


@router.put("/bugs/{bug_id}", response_model=BugOut)
def update_bug(
    bug_id: int,
    bug_in: BugUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_bug = bug_crud.get_bug(db, bug_id)
    if not db_bug or db_bug.project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bug not found")

    updated = bug_crud.update_bug(db, db_bug, bug_in)
    return updated


@router.patch("/bugs/{bug_id}/status", response_model=BugOut)
def update_bug_status(
    bug_id: int,
    status_in: BugStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_bug = bug_crud.get_bug(db, bug_id)
    if not db_bug or db_bug.project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bug not found")

    try:
        updated = bug_crud.update_bug_status(db, db_bug, status_in.status)
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
