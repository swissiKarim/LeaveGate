# scenario-id: US-08/SC-6
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    # Check the new form – all interactive elements have data-testid
    page.goto(base_url + "/employees/new")
    page.wait_for_selector('[data-testid="employee-submit"]')

    visible = {
        "employee-submit": page.is_visible('[data-testid="employee-submit"]'),
    }
    screenshot(page, "US-08/SC-6")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
