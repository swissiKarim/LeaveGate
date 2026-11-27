"""SQLAlchemy model for Employee."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    team: Mapped[str] = mapped_column(String(255), nullable=False)
    remaining_days: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
