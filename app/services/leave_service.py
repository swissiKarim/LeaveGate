"""Domain-Service layer for leave request business rules.

All business rules are enforced here so that invalid states are excluded
at the system level, independent of the HTTP layer.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

#: Allowed status transitions: {from_status: {to_status, ...}}
VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft":     {"submitted", "cancelled"},
    "submitted": {"approved", "rejected"},
    "approved":  {"cancelled"},
    "rejected":  set(),
    "cancelled": set(),
}

ALL_STATUSES = set(VALID_TRANSITIONS.keys())


class InvalidTransitionError(Exception):
    """Raised when a requested status transition is not allowed."""

    def __init__(self, from_status: str, to_status: str) -> None:
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(
            f"Transition from '{from_status}' to '{to_status}' is not allowed."
        )


class BusinessRuleError(Exception):
    """Raised when a business rule is violated (maps to HTTP 409)."""


class ValidationError(Exception):
    """Raised when input data is invalid (maps to HTTP 422)."""


# ---------------------------------------------------------------------------
# Workday calculation (AC-2)
# ---------------------------------------------------------------------------

def count_workdays(start: date, end: date) -> int:
    """Return the number of weekdays (Mon–Fri) between *start* and *end* inclusive.

    Raises ValidationError when the result is zero (e.g. weekend-only range).
    """
    if end < start:
        raise ValidationError(
            f"end_date ({end}) must not be before start_date ({start})."
        )

    total = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Mon … 4=Fri
            total += 1
        current += timedelta(days=1)

    if total == 0:
        raise ValidationError(
            f"Date range {start} – {end} contains no workdays (Mon–Fri). "
            "days must be at least 1."
        )

    return total


# ---------------------------------------------------------------------------
# State-machine transition (AC-1)
# ---------------------------------------------------------------------------

def apply_transition(current_status: str, new_status: str) -> str:
    """Validate and return the new status after a transition.

    Raises InvalidTransitionError if the transition is not in VALID_TRANSITIONS.
    """
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidTransitionError(current_status, new_status)
    return new_status


# ---------------------------------------------------------------------------
# Business rules for creating a leave request
# ---------------------------------------------------------------------------

def validate_new_leave_request(
    *,
    db: "Session",
    employee_id: int,
    leave_type: str,
    start: date,
    end: date,
    days: int,
) -> None:
    """Enforce all business rules when creating a new leave request.

    Rules checked (in order):
    1. days == count_workdays(start, end)  — caller should pass the computed value.
    2. For vacation: days <= employee.remaining_days  (AC-3)
    3. No overlap with submitted/approved requests for the same employee (AC-4)

    Raises:
        ValidationError    – workday count is zero / dates invalid
        BusinessRuleError  – remaining_days exceeded or overlap found
    """
    from app.models import Employee, LeaveRequest  # local import to avoid circular deps

    # AC-3: vacation quota check
    if leave_type == "vacation":
        emp = db.get(Employee, employee_id)
        if emp is None:
            raise BusinessRuleError(f"Employee {employee_id} not found.")
        if days > emp.remaining_days:
            raise BusinessRuleError(
                f"Requested {days} vacation days exceed the employee's "
                f"remaining_days ({emp.remaining_days})."
            )

    # AC-4: overlap check
    blocking_statuses = ("submitted", "approved")
    existing = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status.in_(blocking_statuses),
        )
        .all()
    )
    for req in existing:
        req_start: date = req.start_date
        req_end: date = req.end_date
        # Overlap when not (new_end < req_start or new_start > req_end)
        if not (end < req_start or start > req_end):
            raise BusinessRuleError(
                f"Leave request overlaps with existing request {req.id} "
                f"(status='{req.status}', {req_start} – {req_end})."
            )
