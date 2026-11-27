"""Tests for employee UI routes (US-08)."""


def test_employee_list_page(client):
    resp = client.get("/employees")
    assert resp.status_code == 200
    assert "employee-list" in resp.text


def test_employee_list_page_with_filter_params(client):
    """Filter params q, team, sort, page are supported in URL."""
    resp = client.get("/employees?q=Alice&team=Engineering&sort=name&page=1")
    assert resp.status_code == 200
    assert "employee-list" in resp.text


def test_employee_list_shows_created_employee(client):
    client.post("/api/employees", json={
        "name": "Alice Test", "email": "alice.ui@example.com",
        "team": "Engineering", "remaining_days": 15,
    })
    resp = client.get("/employees")
    assert resp.status_code == 200
    assert "Alice Test" in resp.text


def test_employee_list_filter_q_in_html(client):
    """q param is preserved in URL / filter input value."""
    client.post("/api/employees", json={
        "name": "Alice Filter", "email": "af@example.com",
        "team": "Dev", "remaining_days": 10,
    })
    resp = client.get("/employees?q=Alice")
    assert resp.status_code == 200
    assert "Alice" in resp.text


def test_employee_new_form_page(client):
    resp = client.get("/employees/new")
    assert resp.status_code == 200
    # All required data-testid attributes present
    assert 'data-testid="employee-name"' in resp.text
    assert 'data-testid="employee-email"' in resp.text
    assert 'data-testid="employee-team"' in resp.text
    assert 'data-testid="employee-remaining-days"' in resp.text
    assert 'data-testid="employee-submit"' in resp.text


def test_employee_new_form_has_labels(client):
    resp = client.get("/employees/new")
    assert resp.status_code == 200
    assert "Name" in resp.text
    assert "Email" in resp.text


def test_employee_detail_page(client):
    create_resp = client.post("/api/employees", json={
        "name": "Detail Person", "email": "detail@example.com",
        "team": "QA", "remaining_days": 10,
    })
    emp_id = create_resp.json()["id"]
    resp = client.get(f"/employees/{emp_id}")
    assert resp.status_code == 200
    assert "Detail Person" in resp.text
    assert 'data-testid="employee-detail-card"' in resp.text


def test_employee_detail_not_found(client):
    resp = client.get("/employees/999999")
    assert resp.status_code == 404


def test_employee_edit_form_page(client):
    create_resp = client.post("/api/employees", json={
        "name": "Edit Person", "email": "edit@example.com",
        "team": "Ops", "remaining_days": 5,
    })
    emp_id = create_resp.json()["id"]
    resp = client.get(f"/employees/{emp_id}/edit")
    assert resp.status_code == 200
    # All required data-testid attributes present
    assert 'data-testid="employee-name"' in resp.text
    assert 'data-testid="employee-email"' in resp.text
    assert 'data-testid="employee-team"' in resp.text
    assert 'data-testid="employee-remaining-days"' in resp.text
    assert 'data-testid="employee-submit"' in resp.text
    # Existing data pre-filled
    assert "Edit Person" in resp.text


def test_employee_edit_form_has_labels(client):
    create_resp = client.post("/api/employees", json={
        "name": "Label Test", "email": "label@example.com",
        "team": "Dev", "remaining_days": 20,
    })
    emp_id = create_resp.json()["id"]
    resp = client.get(f"/employees/{emp_id}/edit")
    assert resp.status_code == 200
    assert "Name" in resp.text
    assert "Email" in resp.text


def test_employee_edit_not_found(client):
    resp = client.get("/employees/999999/edit")
    assert resp.status_code == 404


def test_employee_list_has_new_button(client):
    resp = client.get("/employees")
    assert resp.status_code == 200
    assert 'data-testid="employee-new-btn"' in resp.text
