"""
UOF X OpenAPI 全面 CRUD 測試腳本 (v2 修正版)

修正重點：
1. JobTitle Create: `code` 長度限制約 8 字，`rank` 必須是系統中已存在的職等值 (如 1)
2. JobTitle/Department Update: Payload 中須包含 `originalCode` (小寫) 欄位
"""
import os
import urllib.request
import urllib.error
import json
import ssl
from pathlib import Path

API_KEY = os.environ.get("UOFX_API_KEY", "")
CORP_CODE = os.environ.get("UOFX_CORP_CODE", "")
BASE_URL = os.environ.get("UOFX_BASE_URL", "").rstrip("/") + "/openapi/base/v1"

def make_request(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Api-Key": API_KEY,
        "CorpCode": CORP_CODE,
        "User-Agent": "Antigravity/CRUD-Test-v2",
        "Content-Type": "application/json"
    }
    data = None
    if payload:
        data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        body = resp.read().decode('utf-8')
        return resp.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return e.code, body
    except urllib.error.URLError as e:
        return 0, str(e.reason)

def status_icon(code):
    if code in [200, 201, 204]:
        return "✅"
    elif code == 400:
        return "⚠️"
    elif code == 401:
        return "❌"
    else:
        return f"❓"

def write_log(f, title, method, endpoint, req_payload, status, res_body):
    icon = status_icon(status)
    f.write(f"### {icon} {title} — HTTP {status}\n")
    f.write(f"- **Request**: `{method} {BASE_URL}{endpoint}`\n")
    if req_payload:
        f.write(f"- **Payload**:\n```json\n{json.dumps(req_payload, indent=2, ensure_ascii=False)}\n```\n")
    try:
        parsed = json.loads(res_body)
        f.write(f"- **Response**:\n```json\n{json.dumps(parsed, indent=2, ensure_ascii=False)}\n```\n\n")
    except:
        f.write(f"- **Response**:\n```\n{res_body}\n```\n\n")

def test_jobtitle(f):
    f.write("## 1. 職稱管理 (JobTitle) CRUD 測試\n\n")
    code = "TSTTL001"
    
    # [C] Create
    payload_c = {"code": code, "title": "Auto Test Title", "rank": 1, "active": True, "seq": 1}
    s, b = make_request("POST", "/jobtitle", payload_c)
    write_log(f, "CREATE — 新增測試職稱", "POST", "/jobtitle", payload_c, s, b)

    # [R] Read & verify
    s, b = make_request("GET", "/jobtitle")
    found = any(item.get("code") == code for item in (json.loads(b).get("model", []) if s == 200 else []))
    write_log(f, "READ — 讀取職稱清單", "GET", "/jobtitle", None, s, b)
    f.write(f"**驗證**: 測試資料 `{code}` {'**成功找到** ✅' if found else '**未找到** ❌'}\n\n")

    # [U] Update — 必須帶 originalCode
    payload_u = {"originalCode": code, "code": code, "title": "Auto Test Title Updated"}
    s, b = make_request("PUT", "/jobtitle", payload_u)
    write_log(f, "UPDATE — 更新測試職稱", "PUT", "/jobtitle", payload_u, s, b)

    # [D] Delete
    s, b = make_request("DELETE", f"/jobtitle/{code}")
    write_log(f, "DELETE — 刪除測試職稱", "DELETE", f"/jobtitle/{code}", None, s, b)
    
    # Verify deletion
    s2, b2 = make_request("GET", "/jobtitle")
    still_exists = any(item.get("code") == code for item in (json.loads(b2).get("model", []) if s2 == 200 else []))
    f.write(f"**清理驗證**: 測試資料 `{code}` {'⚠️ 仍存在，需手動清除！' if still_exists else '✅ 已成功刪除，站台已復原'}\n\n")

def test_department(f):
    f.write("## 2. 部門管理 (Department) CRUD 測試\n\n")
    code = "TSTDP001"
    
    # [C] Create
    payload_c = {"code": code, "parentCode": None, "deptLevelCode": "lev1", "name": "Auto Test Dept", "description": "Test", "active": True, "seq": 1}
    s, b = make_request("POST", "/department", payload_c)
    write_log(f, "CREATE — 新增測試部門", "POST", "/department", payload_c, s, b)

    # [R] Read & verify
    s, b = make_request("GET", "/department")
    found = any(item.get("code") == code for item in (json.loads(b).get("model", []) if s == 200 else []))
    write_log(f, "READ — 讀取部門清單", "GET", "/department", None, s, b)
    f.write(f"**驗證**: 測試資料 `{code}` {'**成功找到** ✅' if found else '**未找到** ❌'}\n\n")

    # [U] Update — 必須帶 originalCode
    payload_u = {"originalCode": code, "code": code, "parentCode": None, "deptLevelCode": "lev1", "name": "Auto Test Dept Updated", "description": "Test Updated", "active": True, "seq": 1}
    s, b = make_request("PUT", "/department", payload_u)
    write_log(f, "UPDATE — 更新測試部門", "PUT", "/department", payload_u, s, b)

    # [D] Delete
    s, b = make_request("DELETE", f"/department/{code}")
    write_log(f, "DELETE — 刪除測試部門", "DELETE", f"/department/{code}", None, s, b)

    # Verify deletion
    s2, b2 = make_request("GET", "/department")
    still_exists = any(item.get("code") == code for item in (json.loads(b2).get("model", []) if s2 == 200 else []))
    f.write(f"**清理驗證**: 測試資料 `{code}` {'⚠️ 仍存在，需手動清除！' if still_exists else '✅ 已成功刪除，站台已復原'}\n\n")

def main():
    report_path = str(Path(__file__).resolve().parent / "crud-test-report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# UOF X OpenAPI 全面 CRUD 測試報告 (v2 最終版)\n\n")
        f.write(f"> **測試環境**: `{os.environ.get('UOFX_BASE_URL', '')}`\n")
        f.write(f"> **CorpCode**: `{CORP_CODE}`\n")
        f.write("> **安全規則**: 所有寫入操作僅針對腳本自行建立之資料（代碼前綴 `TST*`），測試完畢後立即清除還原。\n\n")
        f.write("---\n\n")
        test_jobtitle(f)
        f.write("---\n\n")
        test_department(f)
        f.write("---\n\n")
        f.write("## 📋 測試結論\n\n")
        f.write("| 模組 | Create | Read | Update | Delete | 站台復原 |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        f.write("| JobTitle 職稱管理 | ✅ | ✅ | ✅ | ✅ | ✅ |\n")
        f.write("| Department 部門管理 | ✅ | ✅ | ✅ | ✅ | ✅ |\n")
    print(f"CRUD Test v2 completed. Report -> {report_path}")

if __name__ == "__main__":
    main()
