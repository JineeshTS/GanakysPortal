"""
Department and Designation models.
WBS Reference: Tasks 3.2.1.1.6, 3.2.1.1.7
"""
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.employee import EmployeeEmployment


class Department(BaseModel):
    """
    Department model.

    WBS Reference: Task 3.2.1.1.6
    Fields: name, code (unique), description, head_employee_id, is_active
    """

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    head_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    designations: Mapped[List["Designation"]] = relationship(
        "Designation",
        back_populates="department",
    )
    employees: Mapped[List["EmployeeEmployment"]] = relationship(
        "EmployeeEmployment",
        back_populates="department",
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, code={self.code}, name={self.name})>"


class Designation(BaseModel):
    """
    Designation/Job Title model.

    WBS Reference: Task 3.2.1.1.7
    Fields: name, code, department_id (nullable), level, is_active
    """

    __tablename__ = "designations"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(
        "Department",
        back_populates="designations",
    )
    employees: Mapped[List["EmployeeEmployment"]] = relationship(
        "EmployeeEmployment",
        back_populates="designation",
    )

    def __repr__(self) -> str:
        return f"<Designation(id={self.id}, code={self.code}, name={self.name})>"
