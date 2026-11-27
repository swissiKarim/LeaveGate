"""SQLAlchemy models package – import all models here so Base.metadata is complete."""
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest

__all__ = ["Employee", "LeaveRequest"]
