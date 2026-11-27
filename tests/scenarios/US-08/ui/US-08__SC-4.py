# scenario-id: US-08/SC-4
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    page.goto(base_url + "/employees/new")
    page.wait_for_selector('[data-testid="employee-name"]')

    visible = {
        "employee-name": page.is_visible('[data-testid="employee-name"]'),
        "employee-email": page.is_visible('[data-testid="employee-email"]'),
        "employee-team": page.is_visible('[data-testid="employee-team"]'),
        "employee-remaining-days": page.is_visible('[data-testid="employee-remaining-days"]'),
        "employee-submit": page.is_visible('[data-testid="employee-submit"]'),
    }
    screenshot(page, "US-08/SC-4")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
