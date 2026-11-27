"""pytest tests covering the domain service layer (AC-1 through AC-5).

Covers:
- All valid and invalid state machine transitions (AC-1)
- Workday calculation including weekends / zero-workday ranges (AC-2)
- Vacation remaining_days quota check (AC-3)
- Overlap detection for submitted/approved requests (AC-4)

These tests use the in-memory DB fixture from tests/conftest.py.
"""
from datetime import date

import pytest

from app.services.leave_service import (
    VALID_TRANSITIONS,
    BusinessRuleError,
    InvalidTransitionError,
    ValidationError,
    apply_transition,
    count_workdays,
    validate_new_leave_request,
)


# ===========================================================================
# AC-1: State machine — apply_transition
# ===========================================================================

class TestStateMachine:
    """All valid and invalid transitions from the spec."""

    # -- Valid transitions --------------------------------------------------

    def test_draft_to_submitted(self):
        assert apply_transition("draft", "submitted") == "submitted"

    def test_draft_to_cancelled(self):
        assert apply_transition("draft", "cancelled") == "cancelled"

    def test_submitted_to_approved(self):
        assert apply_transition("submitted", "approved") == "approved"

    def test_submitted_to_rejected(self):
        assert apply_transition("submitted", "rejected") == "rejected"

    def test_approved_to_cancelled(self):
        assert apply_transition("approved", "cancelled") == "cancelled"

    # -- Invalid transitions ------------------------------------------------

    def test_approved_to_submitted_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("approved", "submitted")

    def test_rejected_to_approved_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("rejected", "approved")

    def test_cancelled_to_draft_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("cancelled", "draft")

    def test_cancelled_to_submitted_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("cancelled", "submitted")

    def test_rejected_to_submitted_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("rejected", "submitted")

    def test_draft_to_approved_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("draft", "approved")

    def test_draft_to_rejected_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("draft", "rejected")

    def test_submitted_to_draft_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("submitted", "draft")

    def test_approved_to_draft_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("approved", "draft")

    def test_approved_to_rejected_raises(self):
        with pytest.raises(InvalidTransitionError):
            apply_transition("approved", "rejected")

    def test_error_contains_statuses(self):
        exc = None
        try:
            apply_transition("approved", "submitted")
        except InvalidTransitionError as e:
            exc = e
        assert exc is not None
        assert "approved" in str(exc)
        assert "submitted" in str(exc)

    def test_valid_transitions_map_completeness(self):
        """VALID_TRANSITIONS covers all five states."""
        assert set(VALID_TRANSITIONS.keys()) == {
            "draft", "submitted", "approved", "rejected", "cancelled"
        }


# ===========================================================================
# AC-2: Workday calculation — count_workdays
# ===========================================================================

class TestCountWorkdays:
    """Workday counting including edge cases."""

    def test_mon_to_fri_is_5(self):
        # 2025-08-04 (Mon) – 2025-08-08 (Fri)
        assert count_workdays(date(2025, 8, 4), date(2025, 8, 8)) == 5

    def test_mon_to_next_fri_spans_weekend(self):
        # 2025-08-04 (Mon) – 2025-08-15 (Fri): two full weeks = 10
        assert count_workdays(date(2025, 8, 4), date(2025, 8, 15)) == 10

    def test_single_monday_is_1(self):
        assert count_workdays(date(2025, 8, 4), date(2025, 8, 4)) == 1

    def test_single_friday_is_1(self):
        assert count_workdays(date(2025, 8, 8), date(2025, 8, 8)) == 1

    def test_weekend_only_raises(self):
        # 2025-08-09 (Sat) – 2025-08-10 (Sun)
        with pytest.raises(ValidationError):
            count_workdays(date(2025, 8, 9), date(2025, 8, 10))

    def test_saturday_only_raises(self):
        with pytest.raises(ValidationError):
            count_workdays(date(2025, 8, 9), date(2025, 8, 9))

    def test_mon_to_next_mon_excludes_weekend(self):
        # 2025-08-04 (Mon) – 2025-08-11 (Mon): 6 workdays (Mon–Fri + Mon)
        assert count_workdays(date(2025, 8, 4), date(2025, 8, 11)) == 6

    def test_end_before_start_raises(self):
        with pytest.raises(ValidationError):
            count_workdays(date(2025, 8, 8), date(2025, 8, 4))

    def test_includes_friday_excludes_saturday(self):
        # Fri + Sat + Sun → only Friday counts
        assert count_workdays(date(2025, 8, 8), date(2025, 8, 10)) == 1

    def test_two_weeks_mon_fri(self):
        # 2025-08-04 to 2025-08-15: exactly 10 workdays
        assert count_workdays(date(2025, 8, 4), date(2025, 8, 15)) == 10


# ===========================================================================
# AC-3: Vacation quota — validate_new_leave_request
# ===========================================================================

class TestVacationQuota:
    """Remaining days check for vacation type."""

    def test_vacation_within_quota_ok(self, db_session):
        from app.models import Employee
        emp = Employee(name="Alice", email="alice@x.com", team="Dev", remaining_days=10)
        db_session.add(emp)
        db_session.flush()

        # 5 workdays, employee has 10 → should not raise
        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_vacation_exact_quota_ok(self, db_session):
        from app.models import Employee
        emp = Employee(name="Bob", email="bob@x.com", team="Dev", remaining_days=5)
        db_session.add(emp)
        db_session.flush()

        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_vacation_exceeds_quota_raises(self, db_session):
        from app.models import Employee
        emp = Employee(name="Carol", email="carol@x.com", team="Dev", remaining_days=3)
        db_session.add(emp)
        db_session.flush()

        with pytest.raises(BusinessRuleError, match="remaining_days"):
            validate_new_leave_request(
                db=db_session,
                employee_id=emp.id,
                leave_type="vacation",
                start=date(2025, 8, 4),
                end=date(2025, 8, 8),
                days=5,
            )

    def test_homeoffice_ignores_quota(self, db_session):
        """homeoffice type does not check remaining_days."""
        from app.models import Employee
        emp = Employee(name="Dave", email="dave@x.com", team="Dev", remaining_days=0)
        db_session.add(emp)
        db_session.flush()

        # Should not raise even though remaining_days=0
        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="homeoffice",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_sick_ignores_quota(self, db_session):
        """sick type does not check remaining_days."""
        from app.models import Employee
        emp = Employee(name="Eve", email="eve@x.com", team="Dev", remaining_days=0)
        db_session.add(emp)
        db_session.flush()

        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="sick",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )


# ===========================================================================
# AC-4: Overlap detection — validate_new_leave_request
# ===========================================================================

class TestOverlapDetection:
    """Overlap check with submitted/approved requests."""

    def _make_employee(self, db, name="Emp", remaining_days=30):
        from app.models import Employee
        emp = Employee(name=name, email=f"{name}@x.com", team="Dev", remaining_days=remaining_days)
        db.add(emp)
        db.flush()
        return emp

    def _make_lr(self, db, emp_id, start, end, status, days=5):
        from app.models import LeaveRequest
        lr = LeaveRequest(
            employee_id=emp_id,
            type="vacation",
            start_date=start,
            end_date=end,
            days=days,
            status=status,
        )
        db.add(lr)
        db.flush()
        return lr

    def test_no_overlap_ok(self, db_session):
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "submitted")

        # New request: different week, no overlap
        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 11),
            end=date(2025, 8, 15),
            days=5,
        )

    def test_overlap_with_submitted_raises(self, db_session):
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "submitted")

        with pytest.raises(BusinessRuleError, match="overlap"):
            validate_new_leave_request(
                db=db_session,
                employee_id=emp.id,
                leave_type="vacation",
                start=date(2025, 8, 6),
                end=date(2025, 8, 12),
                days=5,
            )

    def test_overlap_with_approved_raises(self, db_session):
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "approved")

        with pytest.raises(BusinessRuleError, match="overlap"):
            validate_new_leave_request(
                db=db_session,
                employee_id=emp.id,
                leave_type="vacation",
                start=date(2025, 8, 4),
                end=date(2025, 8, 8),
                days=5,
            )

    def test_overlap_with_draft_allowed(self, db_session):
        """Draft requests do not block new overlapping requests."""
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "draft")

        # Should not raise
        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_overlap_with_rejected_allowed(self, db_session):
        """Rejected requests do not block new overlapping requests."""
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "rejected")

        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_overlap_with_cancelled_allowed(self, db_session):
        """Cancelled requests do not block new overlapping requests."""
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "cancelled")

        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )

    def test_adjacent_dates_not_overlap(self, db_session):
        """Requests that touch at boundaries but don't overlap are allowed."""
        emp = self._make_employee(db_session)
        self._make_lr(db_session, emp.id,
                      date(2025, 8, 4), date(2025, 8, 8), "submitted")

        # Starts the day after existing ends → no overlap
        validate_new_leave_request(
            db=db_session,
            employee_id=emp.id,
            leave_type="vacation",
            start=date(2025, 8, 9),
            end=date(2025, 8, 15),
            days=5,
        )

    def test_different_employee_no_overlap_check(self, db_session):
        """Overlap check is per-employee; different employees are independent."""
        emp1 = self._make_employee(db_session, "Emp1")
        emp2 = self._make_employee(db_session, "Emp2")
        self._make_lr(db_session, emp1.id,
                      date(2025, 8, 4), date(2025, 8, 8), "submitted")

        # Same dates but different employee → should not raise
        validate_new_leave_request(
            db=db_session,
            employee_id=emp2.id,
            leave_type="vacation",
            start=date(2025, 8, 4),
            end=date(2025, 8, 8),
            days=5,
        )


# ===========================================================================
# AC-1 (HTTP layer): Status transition via API endpoint
# ===========================================================================

class TestStatusTransitionAPI:
    """Integration tests via FastAPI test client."""

    def _create_employee(self, client, remaining_days=30):
        resp = client.post("/api/employees", json={
            "name": "Test Emp", "email": "t@x.com",
            "team": "Dev", "remaining_days": remaining_days,
        })
        assert resp.status_code == 201
        return resp.json()["id"]

    def _create_lr(self, client, emp_id, start="2025-09-01", end="2025-09-05",
                   leave_type="sick"):
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": leave_type,
            "start_date": start,
            "end_date": end,
        })
        assert resp.status_code == 201
        return resp.json()

    def test_transition_draft_to_submitted(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "submitted"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "submitted"

    def test_transition_submitted_to_approved(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "submitted"})
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "approved"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    def test_transition_submitted_to_rejected(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "submitted"})
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "rejected"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    def test_transition_approved_to_cancelled(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "submitted"})
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "approved"})
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "cancelled"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_transition_draft_to_cancelled(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "cancelled"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_invalid_transition_returns_409(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "submitted"})
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "approved"})
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "submitted"})
        assert resp.status_code == 409
        body = resp.json()
        assert "error" in body or "error" in body.get("detail", {})

    def test_invalid_transition_rejected_to_approved_returns_409(self, client):
        emp_id = self._create_employee(client)
        lr = self._create_lr(client, emp_id)
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "submitted"})
        client.post(f"/api/leave-requests/{lr['id']}/status",
                    json={"status": "rejected"})
        resp = client.post(f"/api/leave-requests/{lr['id']}/status",
                           json={"status": "approved"})
        assert resp.status_code == 409
        body = resp.json()
        assert "error" in body or "error" in body.get("detail", {})


# ===========================================================================
# AC-2 (HTTP layer): days computed by API
# ===========================================================================

class TestWorkdaysAPI:
    def _create_employee(self, client):
        resp = client.post("/api/employees", json={
            "name": "WD Emp", "email": "wd@x.com",
            "team": "Dev", "remaining_days": 30,
        })
        return resp.json()["id"]

    def test_mon_fri_gives_5(self, client):
        emp_id = self._create_employee(client)
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-08-04",
            "end_date": "2025-08-08",
        })
        assert resp.status_code == 201
        assert resp.json()["days"] == 5

    def test_weekend_range_returns_422(self, client):
        emp_id = self._create_employee(client)
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-08-09",
            "end_date": "2025-08-10",
        })
        assert resp.status_code == 422

    def test_mon_to_next_mon_gives_6(self, client):
        emp_id = self._create_employee(client)
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-08-04",
            "end_date": "2025-08-11",
        })
        assert resp.status_code == 201
        assert resp.json()["days"] == 6


# ===========================================================================
# AC-3 (HTTP layer): Vacation quota via API
# ===========================================================================

class TestVacationQuotaAPI:
    def test_within_quota_accepted(self, client):
        resp = client.post("/api/employees", json={
            "name": "Q Emp", "email": "q@x.com", "team": "Dev", "remaining_days": 10,
        })
        emp_id = resp.json()["id"]
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "vacation",
            "start_date": "2025-08-04",
            "end_date": "2025-08-08",
        })
        assert resp.status_code == 201

    def test_exceeds_quota_returns_409(self, client):
        resp = client.post("/api/employees", json={
            "name": "Q2 Emp", "email": "q2@x.com", "team": "Dev", "remaining_days": 3,
        })
        emp_id = resp.json()["id"]
        resp = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "vacation",
            "start_date": "2025-08-04",
            "end_date": "2025-08-08",
        })
        assert resp.status_code == 409
        body = resp.json()
        assert "error" in body or "error" in body.get("detail", {})


# ===========================================================================
# AC-4 (HTTP layer): Overlap via API
# ===========================================================================

class TestOverlapAPI:
    def test_overlap_submitted_returns_409(self, client):
        resp = client.post("/api/employees", json={
            "name": "O Emp", "email": "o@x.com", "team": "Dev", "remaining_days": 30,
        })
        emp_id = resp.json()["id"]
        # Create first request and submit it
        r1 = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-09-01",
            "end_date": "2025-09-05",
        })
        assert r1.status_code == 201
        client.post(f"/api/leave-requests/{r1.json()['id']}/status",
                    json={"status": "submitted"})

        # Second overlapping request
        r2 = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-09-03",
            "end_date": "2025-09-10",
        })
        assert r2.status_code == 409
        body = r2.json()
        assert "error" in body or "error" in body.get("detail", {})

    def test_overlap_approved_returns_409(self, client):
        resp = client.post("/api/employees", json={
            "name": "O2 Emp", "email": "o2@x.com", "team": "Dev", "remaining_days": 30,
        })
        emp_id = resp.json()["id"]
        r1 = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-09-01",
            "end_date": "2025-09-05",
        })
        assert r1.status_code == 201
        client.post(f"/api/leave-requests/{r1.json()['id']}/status",
                    json={"status": "submitted"})
        client.post(f"/api/leave-requests/{r1.json()['id']}/status",
                    json={"status": "approved"})

        r2 = client.post("/api/leave-requests", json={
            "employee_id": emp_id,
            "type": "sick",
            "start_date": "2025-09-01",
            "end_date": "2025-09-05",
        })
        assert r2.status_code == 409
        body = r2.json()
        assert "error" in body or "error" in body.get("detail", {})
