from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship

from backend.db.session import Base


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    severity = Column(String, nullable=False, default="medium")  # low, medium, high, critical
    priority = Column(String, nullable=False, default="medium")  # low, medium, high
    status = Column(String, nullable=False, default="open")      # open, in_progress, resolved, closed

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="bugs")
    # We keep user relationships simple for now
