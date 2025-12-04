from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from backend.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="tester")  # tester, developer, admin

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
