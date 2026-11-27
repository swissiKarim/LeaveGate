# scenario-id: US-08/SC-1
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    page.goto(base_url + "/employees")
    page.wait_for_selector('[data-testid="employee-list"]')
    visible = {
        "employee-list": page.is_visible('[data-testid="employee-list"]'),
    }
    screenshot(page, "US-08/SC-1")
    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
