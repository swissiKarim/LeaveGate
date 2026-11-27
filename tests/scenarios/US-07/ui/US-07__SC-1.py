# scenario-id: US-07/SC-1
"""SC-1: Sidebar contains navigation links with data-testid attributes."""
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    visible = {
        "nav-dashboard": page.is_visible('[data-testid="nav-dashboard"]'),
        "nav-employees": page.is_visible('[data-testid="nav-employees"]'),
        "nav-leave-requests": page.is_visible('[data-testid="nav-leave-requests"]'),
    }

    screenshot(page, "US-07/SC-1")

    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
