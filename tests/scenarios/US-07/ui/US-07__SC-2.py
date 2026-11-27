# scenario-id: US-07/SC-2
"""SC-2: Header shows page title and global search field."""
import json

from asb_ui import page_session, screenshot

with page_session() as (page, base_url):
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    visible = {
        "global-search": page.is_visible('[data-testid="global-search"]'),
    }

    screenshot(page, "US-07/SC-2")

    print(json.dumps({
        "title": page.title(),
        "url": page.url,
        "text": page.inner_text("body"),
        "visible": visible,
    }))
