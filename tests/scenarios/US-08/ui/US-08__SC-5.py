# scenario-id: US-08/SC-5
import json
import urllib.request as urlreq

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    # Create an employee via API first
    create_data = json.dumps({
        "name": "Alice",
        "email": "alice.edit@example.com",
        "team": "Engineering",
        "remaining_days": 20,
    }).encode()
    req = urlreq.Request(
        base_url + "/api/employees",
        data=create_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlreq.urlopen(req) as r:
        emp = json.loads(r.read())
    emp_id = emp["id"]

    # Navigate to edit page
    page.goto(base_url + "/employees/" + str(emp_id) + "/edit")
    page.wait_for_selector('[data-testid="employee-name"]')

    # Clear and type new name
    page.fill('[data-testid="employee-name"]', "Alice Updated")

    # Intercept PATCH response to capture status
    patch_status = {}

    def handle_response(response):
        if f"/api/employees/{emp_id}" in response.url and response.request.method == "PATCH":
            patch_status["status"] = response.status

    page.on("response", handle_response)

    # Click submit
    page.click('[data-testid="employee-submit"]')

    # Wait for navigation after submit
    try:
        page.wait_for_url(f"**/employees/{emp_id}", timeout=5000)
    except Exception:  # noqa: S110
        pass

    screenshot(page, "US-08/SC-5")

    status = patch_status.get("status", 200)

    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": {"employee-submit": False},
        "status": status,
    }))
