"""Tests for SQLAlchemy models and in-memory DB fixture (AC-1, AC-3, AC-4)."""
from datetime import date

from app.database import Base, SessionLocal, get_db
from app.models import Employee, LeaveRequest


# AC-1: Employee model has all required fields
def test_employee_model_fields():
    cols = {c.name for c in Employee.__table__.columns}
    assert {"id", "name", "email", "team", "remaining_days"}.issubset(cols)


# AC-1: LeaveRequest model has all required fields
def test_leave_request_model_fields():
    cols = {c.name for c in LeaveRequest.__table__.columns}
    assert {
        "id", "employee_id", "type", "start_date", "end_date",
        "days", "reason", "status",
    }.issubset(cols)


# AC-3: app/database.py provides central session factory
def test_session_factory_importable():
    assert SessionLocal is not None
    assert get_db is not None


# AC-4: in-memory fixture creates tables and allows CRUD
def test_in_memory_employee_crud(db_session):
    emp = Employee(name="Test User", email="test@example.com", team="QA", remaining_days=15)
    db_session.add(emp)
    db_session.flush()
    fetched = db_session.get(Employee, emp.id)
    assert fetched is not None
    assert fetched.name == "Test User"
    assert fetched.remaining_days == 15


def test_in_memory_leave_request_crud(db_session):
    emp = Employee(name="LR User", email="lr@example.com", team="Dev", remaining_days=20)
    db_session.add(emp)
    db_session.flush()

    lr = LeaveRequest(
        employee_id=emp.id,
        type="vacation",
        start_date=date(2025, 8, 4),
        end_date=date(2025, 8, 8),
        days=5,
        reason="Summer holiday",
        status="draft",
    )
    db_session.add(lr)
    db_session.flush()

    fetched = db_session.get(LeaveRequest, lr.id)
    assert fetched is not None
    assert fetched.type == "vacation"
    assert fetched.status == "draft"


# AC-4: Base is importable from app.database and has correct tables
def test_base_importable():
    assert Base is not None
    assert "employees" in Base.metadata.tables
    assert "leave_requests" in Base.metadata.tables
