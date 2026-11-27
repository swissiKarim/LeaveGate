"""pytest tests covering all four employee API endpoints (US-04, AC-1 to AC-5)."""


# ---------------------------------------------------------------------------
# AC-1: GET /api/employees – list with filter support
# ---------------------------------------------------------------------------

def test_list_employees_empty(client):
    resp = client.get("/api/employees")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_list_employees_returns_created(client):
    client.post("/api/employees", json={
        "name": "Alice Smith", "email": "alice@example.com",
        "team": "Engineering", "remaining_days": 15,
    })
    resp = client.get("/api/employees")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(e["name"] == "Alice Smith" for e in items)


def test_list_employees_filter_team(client):
    client.post("/api/employees", json={
        "name": "Bob Jones", "email": "bob@example.com",
        "team": "Engineering", "remaining_days": 10,
    })
    client.post("/api/employees", json={
        "name": "Carol HR", "email": "carol@example.com",
        "team": "HR", "remaining_days": 20,
    })
    resp = client.get("/api/employees?team=Engineering")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(e["team"] == "Engineering" for e in items)


def test_list_employees_filter_q(client):
    client.post("/api/employees", json={
        "name": "Alice Wonder", "email": "alicew@example.com",
        "team": "Dev", "remaining_days": 12,
    })
    resp = client.get("/api/employees?q=Alice")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any("Alice" in e["name"] for e in items)


def test_list_employees_sort_param(client):
    resp = client.get("/api/employees?sort=name")
    assert resp.status_code == 200


def test_list_employees_page_param(client):
    resp = client.get("/api/employees?page=1")
    assert resp.status_code == 200
    assert "items" in resp.json()


# ---------------------------------------------------------------------------
# AC-2: POST /api/employees – create with validation
# ---------------------------------------------------------------------------

def test_create_employee_success(client):
    resp = client.post("/api/employees", json={
        "name": "Dave Test", "email": "dave@example.com",
        "team": "QA", "remaining_days": 20,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Dave Test"
    assert data["email"] == "dave@example.com"
    assert data["team"] == "QA"
    assert data["remaining_days"] == 20


def test_create_employee_missing_name(client):
    resp = client.post("/api/employees", json={
        "email": "nname@example.com", "team": "Dev", "remaining_days": 10,
    })
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_create_employee_missing_email(client):
    resp = client.post("/api/employees", json={
        "name": "No Email", "team": "Dev", "remaining_days": 10,
    })
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_create_employee_missing_team(client):
    resp = client.post("/api/employees", json={
        "name": "No Team", "email": "noteam@example.com", "remaining_days": 10,
    })
    assert resp.status_code == 422
    assert "error" in resp.json()


def test_create_employee_default_remaining_days(client):
    resp = client.post("/api/employees", json={
        "name": "Eve Default", "email": "eve@example.com", "team": "Ops",
    })
    assert resp.status_code == 201
    assert resp.json()["remaining_days"] == 20


# ---------------------------------------------------------------------------
# AC-3: GET /api/employees/{id} – single employee or 404
# ---------------------------------------------------------------------------

def test_get_employee_by_id(client):
    create_resp = client.post("/api/employees", json={
        "name": "Frank", "email": "frank@example.com",
        "team": "Infra", "remaining_days": 8,
    })
    emp_id = create_resp.json()["id"]
    resp = client.get(f"/api/employees/{emp_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == emp_id
    assert data["name"] == "Frank"


def test_get_employee_not_found(client):
    resp = client.get("/api/employees/999999")
    assert resp.status_code == 404
    assert "error" in resp.json()


# ---------------------------------------------------------------------------
# AC-4: PATCH /api/employees/{id} – partial update
# ---------------------------------------------------------------------------

def test_patch_employee_remaining_days(client):
    create_resp = client.post("/api/employees", json={
        "name": "Grace", "email": "grace@example.com",
        "team": "Design", "remaining_days": 20,
    })
    emp_id = create_resp.json()["id"]
    resp = client.patch(f"/api/employees/{emp_id}", json={"remaining_days": 10})
    assert resp.status_code == 200
    assert resp.json()["remaining_days"] == 10


def test_patch_employee_name(client):
    create_resp = client.post("/api/employees", json={
        "name": "Hank Old", "email": "hank@example.com",
        "team": "Sales", "remaining_days": 5,
    })
    emp_id = create_resp.json()["id"]
    resp = client.patch(f"/api/employees/{emp_id}", json={"name": "Hank New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Hank New"


def test_patch_employee_not_found(client):
    resp = client.patch("/api/employees/999999", json={"remaining_days": 5})
    assert resp.status_code == 404
    assert "error" in resp.json()


# ---------------------------------------------------------------------------
# AC-5: 404 error format contains "error" key
# ---------------------------------------------------------------------------

def test_404_contains_error_key(client):
    resp = client.get("/api/employees/999999")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
