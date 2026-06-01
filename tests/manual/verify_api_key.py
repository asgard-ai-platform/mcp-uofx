import urllib.request
import urllib.error
import re
import json
import ssl
import os
from pathlib import Path

def fetch_api(endpoint):
    # Prepare URL
    base_url = os.environ.get("UOFX_BASE_URL", "").rstrip("/")
    if not base_url:
        raise RuntimeError("UOFX_BASE_URL is required")
    # Replace {version} with 1, and other variables with 'test'
    path = endpoint.replace("{version}", "1")
    path = re.sub(r'\{[^}]+\}', 'test', path)
    url = base_url + path
    
    headers = {
        "Api-Key": os.environ.get("UOFX_API_KEY", ""),
        "CorpCode": os.environ.get("UOFX_CORP_CODE", ""),
        "User-Agent": "Antigravity/1.0"
    }
    
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return resp.getcode(), "OK"
    except urllib.error.HTTPError as e:
        # Check if the error body is a JSON from the API framework
        body = e.read().decode('utf-8')
        try:
            data = json.loads(body)
            # if it's UOF X standard error JSON
            if "errorCode" in data:
                return e.code, f"API Error: {data['errorCode']}"
            return e.code, "HTTP Error"
        except Exception:
            return e.code, "HTTP Error"
    except urllib.error.URLError as e:
        return 0, str(e.reason)

def main():
    root = Path(__file__).resolve().parents[2]
    md_file = os.environ.get("UOFX_API_SPEC_MD", str(root / "docs" / "internal" / "api-spec-and-boundaries.md"))
    out_file = str(Path(__file__).resolve().parent / "api-key-test-report.md")
    
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    results = []
    
    for line in lines:
        match = re.search(r'\|\s*`GET\s([^`]+)`\s*\|\s*([^|]+)\s*\|', line)
        if match:
            endpoint = match.group(1).strip()
            desc = match.group(2).strip()
            
            print(f"Testing {endpoint} ...")
            code, message = fetch_api(endpoint)
            print(f"  -> {code} {message}")
            
            # If code is 401, it's unauthorized. If it's anything else (200, 400, 404),
            # it means the request reached the module and was processed (or param missing),
            # meaning API Key has access to the module!
            if code == 401:
                status_icon = "❌ 未開通 (401)"
            elif code in [200, 204]:
                status_icon = "✅ 成功連通 (200)"
            elif code == 400:
                status_icon = "⚠️ 參數錯誤，但已連通 (400)"
            elif code == 404 and "API Error: 404" in message:
                status_icon = "⚠️ 找不到資源，但已連通 (404)"
            elif code == 500:
                status_icon = "⚠️ 伺服器錯誤，但已連通 (500)"
            else:
                status_icon = f"❓ 其他狀態 ({code})"
                
            results.append((endpoint, desc, code, status_icon))
            
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# API 金鑰權限測試報告\n\n")
        f.write(f"**測試環境**: `{os.environ.get('UOFX_BASE_URL', '')}`\n")
        f.write("**測試條件**: 僅針對 OpenAPI 之 `GET` 請求端點發送，並帶入測試用的 Path 參數。\n\n")
        f.write("| API Endpoint | 描述 | HTTP 狀態碼 | 權限測試結果 |\n")
        f.write("| :--- | :--- | :---: | :--- |\n")
        for res in results:
            f.write(f"| `{res[0]}` | {res[1]} | {res[2]} | {res[3]} |\n")
            
    print(f"\nDone! Report written to {out_file}")

if __name__ == "__main__":
    main()
