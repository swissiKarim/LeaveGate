# scenario-id: US-05/SC-8
"""SC-8: days calculated as 5 workdays for Mon–Fri week."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))


def _post(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


status, emp = _post(f"{base_url}/api/employees",
                    {"name": "SC8 Emp", "email": "sc8@x.com", "team": "Dev", "remaining_days": 20})
# 2025-08-04 (Mon) to 2025-08-08 (Fri) = 5 workdays
status, body = _post(f"{base_url}/api/leave-requests",
                     {"employee_id": emp["id"], "type": "sick",
                      "start_date": "2025-08-04", "end_date": "2025-08-08"})

print(json.dumps({"status": status, "body": body}))
