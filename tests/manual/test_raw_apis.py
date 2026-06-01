import os
import sys
from pprint import pprint
import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mcp_uofx.api_client import uofx_client

TEST_USER = os.getenv("UOFX_TEST_USER", "test_user")
TEST_DEPT_CODE = os.getenv("UOFX_TEST_DEPT_CODE", "TEST_DEPT")

def test_get(url):
    print(f"\nGET {url}")
    try:
        res = uofx_client.get(url)
        print("Success:")
        pprint(res)
    except httpx.HTTPStatusError as e:
        print("HTTP Error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("Error:", e)

def test_post(url, payload):
    print(f"\nPOST {url}")
    print("Payload:", payload)
    try:
        res = uofx_client.post(url, payload=payload)
        print("Success:")
        pprint(res)
    except httpx.HTTPStatusError as e:
        print("HTTP Error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("Error:", e)

print("--- get_form_fields ---")
test_get("/openapi/bpm/v1/form/fields/TEST_FORM")

print("--- get_my_punch_history ---")
test_post("/openapi/eip/v1/punch/personal/history", {
    "user": {"userType": 0, "userCode": TEST_USER},
    "dateRange": {"since": "2026-05-01T00:00:00+08:00", "until": "2026-05-31T23:59:59+08:00"},
    "pageOptions": {"page": 0, "size": 100}
})

print("--- get_dept_punch_report ---")
test_post("/openapi/eip/v1/punch/dept/history", {
    "deptCode": TEST_DEPT_CODE,
    "includeSubDept": False,
    "dateRange": {"since": "2026-05-01T00:00:00+08:00", "until": "2026-05-31T23:59:59+08:00"},
    "pageOptions": {"page": 0, "size": 100}
})

print("--- list_dms_folders ---")
test_get("/openapi/dms/v1/iso/folder/list/ISO-001")

print("--- search_dms_document ---")
test_post("/openapi/dms/v1/doc/list", {
    "keyword": "請假",
    "folderCodeOrId": None,
    "category": 0,
    "pageOptions": {"page": 0, "size": 50}
})
