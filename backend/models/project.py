from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
