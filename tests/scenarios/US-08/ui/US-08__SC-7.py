# scenario-id: US-08/SC-7
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    page.goto(base_url + "/employees/new")
    page.wait_for_selector('[data-testid="employee-name"]')

    body_text = page.inner_text("body")
    screenshot(page, "US-08/SC-7")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": body_text,
        "visible": {"employee-submit": page.is_visible('[data-testid="employee-submit"]')},
    }))
