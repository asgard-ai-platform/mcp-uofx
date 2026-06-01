#!/usr/bin/env python3
"""
UOF X OAuth 登入 CLI — 獨立的 OAuth 登入工具

用法：
    uv run mcp-uofx-login           # 一般登入（自動開啟瀏覽器）
    uv run mcp-uofx-login --status  # 查看目前登入狀態
    uv run mcp-uofx-login --logout  # 清除已儲存的憑證

設計理念：
    仿 `gcloud auth login` / `kubectl login` / `gh auth login` 的獨立 CLI 風格。
    登入完成後，憑證寫入 ~/.uofx/credentials.json。
    MCP Server 每次 tool 呼叫時會自動熱讀取該檔案，無需重啟。
"""

import os
import sys
import time
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ── 載入 .env ────────────────────────────────────────────────────
for env_path in (Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"):
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

# ── 設定常數 ────────────────────────────────────────────────────
CALLBACK_PORT = 3000
CALLBACK_URI = f"http://localhost:{CALLBACK_PORT}"
BASE_URL = os.getenv("UOFX_BASE_URL", "").rstrip("/")
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
VERIFY_SSL = os.getenv("UOFX_VERIFY_SSL", "true").lower() == "true"
SCOPES = "bpm.tasks.read bpm.form.read bpm.form.apply bpm.form.approval dms.all.read dms.all.write base.profile.read"

from .auth import write_credentials, read_credentials, clear_credentials, CREDENTIALS_FILE


# ── OAuth Callback Handler ──────────────────────────────────────
class _CallbackHandler(BaseHTTPRequestHandler):
    """臨時 HTTP Server，接收 OAuth redirect 並交換 token"""

    auth_result = None  # class-level: 用來傳遞結果到主線程

    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if "code" not in params:
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("❌ 缺少授權碼 (authorization code)".encode("utf-8"))
            return

        code = params["code"][0]
        print(f"\n📥 收到授權碼，正在交換 Access Token...")

        try:
            import httpx
            response = httpx.post(
                f"{BASE_URL}/api/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": CALLBACK_URI,
                    "scope": SCOPES,
                },
                verify=VERIFY_SSL,
                timeout=15.0,
            )
            response.raise_for_status()
            token_data = response.json()

            access_token = token_data.get("access_token", "")
            refresh_token = token_data.get("refresh_token", "")
            expires_in = token_data.get("expires_in", 3600)

            if not access_token:
                raise ValueError(f"回應中沒有 access_token: {token_data}")

            # 寫入 ~/.uofx/credentials.json
            write_credentials(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                user_code="current_user",
                base_url=BASE_URL,
            )

            _CallbackHandler.auth_result = "success"
            self._send_html(
                200,
                "✅ UOF X 授權成功！",
                f"Access Token 已寫入 <code>~/.uofx/credentials.json</code>，效期 {expires_in // 60} 分鐘。<br>"
                "您可以安全地關閉此視窗，回到終端機或 IDE 繼續使用 AI 助理。",
                "#4CAF50",
            )
            print(f"✅ 登入成功！Token 已寫入 {CREDENTIALS_FILE} (效期 {expires_in // 60} 分鐘)")

        except Exception as e:
            _CallbackHandler.auth_result = "error"
            self._send_html(
                500,
                "❌ Token 交換失敗",
                f"錯誤訊息：<pre>{str(e)}</pre><br>請檢查 OAuth Client 設定後重試。",
                "#F44336",
            )
            print(f"❌ Token 交換失敗: {e}")

    def _send_html(self, status: int, title: str, body: str, color: str):
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="utf-8"><title>{title}</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; padding: 60px 20px; background: #fafafa;">
    <div style="max-width: 480px; margin: 0 auto; padding: 40px; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
        <h1 style="color: {color}; font-size: 1.5em;">{title}</h1>
        <p style="color: #666; line-height: 1.6;">{body}</p>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # 靜默 HTTP log


# ── CLI 主程式 ──────────────────────────────────────────────────
def do_login():
    """執行 OAuth 登入流程"""
    if not BASE_URL:
        print("❌ 請先在 .env 中設定 UOFX_BASE_URL")
        sys.exit(1)

    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ 請先在 .env 中設定 OAUTH_CLIENT_ID 和 OAUTH_CLIENT_SECRET")
        sys.exit(1)

    # 構建 OAuth 授權 URL
    scope_encoded = urllib.parse.quote(SCOPES, safe="")
    redirect_encoded = urllib.parse.quote(CALLBACK_URI, safe="")
    auth_url = (
        f"{BASE_URL}/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={redirect_encoded}"
        f"&scope={scope_encoded}"
        f"&state=cli_login"
    )

    print("🔐 UOF X OAuth 登入")
    print("─" * 50)
    print(f"📂 憑證將儲存於: {CREDENTIALS_FILE}")
    print(f"🌐 Callback Server: {CALLBACK_URI}")
    print()

    # 啟動臨時 callback server
    try:
        server = HTTPServer(("127.0.0.1", CALLBACK_PORT), _CallbackHandler)
    except OSError as e:
        print(f"❌ 無法綁定 port {CALLBACK_PORT}: {e}")
        print(f"   請確認沒有其他程式佔用此 port (lsof -i :{CALLBACK_PORT})")
        sys.exit(1)

    # 自動開啟瀏覽器
    print("🌐 正在開啟瀏覽器進行登入...")
    print(f"   若瀏覽器未自動開啟，請手動前往：\n   {auth_url}\n")
    webbrowser.open(auth_url)

    # 等待 callback（單次）
    print("⏳ 等待授權回調... (Ctrl+C 取消)")
    try:
        while _CallbackHandler.auth_result is None:
            server.handle_request()
    except KeyboardInterrupt:
        print("\n🚫 已取消登入。")
        sys.exit(1)
    finally:
        server.server_close()

    if _CallbackHandler.auth_result == "success":
        print("\n🎉 登入完成！您現在可以使用 MCP 工具了。")
    else:
        print("\n❌ 登入失敗，請重試。")
        sys.exit(1)


def do_status():
    """顯示目前登入狀態"""
    print("🔐 UOF X 登入狀態")
    print("─" * 50)
    print(f"📂 憑證路徑: {CREDENTIALS_FILE}")

    creds = read_credentials()
    if creds is None:
        if os.path.exists(CREDENTIALS_FILE):
            # 檔案存在但 token 無效
            try:
                with open(CREDENTIALS_FILE, "r") as f:
                    data = json.load(f)
                expires_at = data.get("expires_at", 0)
                expired_ago = time.time() - expires_at
                print(f"⏰ 狀態: Token 已過期 ({expired_ago:.0f} 秒前)")
            except Exception:
                print("❌ 狀態: 憑證檔損毀")
        else:
            print("❌ 狀態: 尚未登入")
        print(f"\n💡 執行 `uv run mcp-uofx-login` 進行登入")
    else:
        expires_at = creds.get("expires_at", 0)
        ttl = expires_at - time.time()
        issued_at = creds.get("issued_at", 0)
        user_code = creds.get("user_code", "N/A")
        base_url = creds.get("base_url", "N/A")

        print(f"✅ 狀態: 已登入")
        print(f"👤 使用者: {user_code}")
        print(f"🌐 伺服器: {base_url}")
        print(f"🔑 Token 長度: {len(creds.get('access_token', ''))} chars")
        print(f"⏰ 剩餘效期: {ttl / 60:.1f} 分鐘")

        if issued_at:
            issued_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(issued_at))
            print(f"📅 發行時間: {issued_str}")


def do_logout():
    """清除已儲存的憑證"""
    print("🔐 UOF X 登出")
    print("─" * 50)
    if os.path.exists(CREDENTIALS_FILE):
        clear_credentials()
        print("✅ 已清除憑證。")
    else:
        print("ℹ️ 尚未登入，無需登出。")


def main():
    if "--status" in sys.argv:
        do_status()
    elif "--logout" in sys.argv:
        do_logout()
    else:
        do_login()


if __name__ == "__main__":
    main()
