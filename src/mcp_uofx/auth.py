"""
UOF X MCP Server — 憑證管理模組

設計理念：仿 kubectl / git credential 模式
- 憑證統一儲存在 ~/.uofx/credentials.json
- MCP Server 本身不持有任何 auth 狀態（無狀態）
- 每次 tool 呼叫時從磁碟「熱讀取」credentials.json
- 登入流程由獨立 CLI (`mcp-uofx-login`) 執行，與 MCP Server 完全解耦
"""

import os
import time
import json
import stat
from functools import wraps

# ── 路徑常數 ──────────────────────────────────────────────────────
CREDENTIALS_DIR = os.path.join(os.path.expanduser("~"), ".uofx")
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")


def _ensure_credentials_dir():
    """確保 ~/.uofx/ 目錄存在，權限 0700"""
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR, mode=0o700, exist_ok=True)
        print(f"[auth] 已建立憑證目錄: {CREDENTIALS_DIR}")


def read_credentials() -> dict | None:
    """
    從磁碟熱讀取 ~/.uofx/credentials.json。
    每次呼叫都直接讀檔，不做記憶體快取。

    Returns:
        有效的 credential dict，或 None（檔案不存在 / 格式錯誤 / token 已過期）
    """
    if not os.path.exists(CREDENTIALS_FILE):
        return None

    try:
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[auth] ❌ 讀取憑證檔失敗: {e}")
        return None

    # 驗證必要欄位
    access_token = data.get("access_token")
    expires_at = data.get("expires_at", 0)

    if not access_token:
        return None

    # TTL 檢查（保留 60 秒緩衝）
    if time.time() >= (expires_at - 60):
        print(f"[auth] ⏰ Token 已過期 (expires_at={expires_at}, now={time.time():.0f})")
        return None

    return data


def write_credentials(
    access_token: str,
    refresh_token: str,
    expires_in: int,
    user_code: str = "current_user",
    base_url: str = "",
):
    """
    將 OAuth token 寫入 ~/.uofx/credentials.json。
    由獨立的 `mcp-uofx-login` CLI 呼叫。

    檔案權限設為 0600（僅擁有者可讀寫），與 ~/.kube/config 相同慣例。
    """
    _ensure_credentials_dir()

    now = time.time()
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": now + expires_in,
        "expires_in": expires_in,
        "issued_at": now,
        "user_code": user_code,
        "base_url": base_url,
    }

    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 設定檔案權限 0600
    os.chmod(CREDENTIALS_FILE, stat.S_IRUSR | stat.S_IWUSR)

    print(f"[auth] ✅ 憑證已寫入 {CREDENTIALS_FILE} (expires_in={expires_in}s)")


def get_access_token() -> str | None:
    """
    取得當前有效的 access_token，供 api_client.py 使用。
    每次呼叫都會從磁碟熱讀取。
    """
    creds = read_credentials()
    if creds is None:
        return None
    return creds.get("access_token")


def clear_credentials():
    """清除本地憑證檔"""
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)
        print(f"[auth] 🗑️ 已清除憑證: {CREDENTIALS_FILE}")


def require_auth(func):
    """
    MCP Tool 攔截器 (Interceptor)：
    在執行 Tool 前從磁碟熱讀取 credential，驗證是否有效。
    若無效，則攔截請求並引導使用者進行登入。

    注意：每次 tool 呼叫都會重新讀檔，不依賴記憶體快取。
    這使得外部的 `mcp-uofx-login` 完成登入後，MCP Server 無需重啟即可感知。
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 檢查是否啟用開發者模式 (Dev Mode 允許使用 API Key 繞過 OAuth)
        dev_mode = os.getenv("UOFX_DEV_MODE", "true").lower() == "true"

        if not dev_mode and read_credentials() is None:
            return (
                "🔒 **權限錯誤**：您的 OAuth 身分驗證已過期或尚未登入。\n\n"
                "請在終端機執行以下指令完成登入：\n"
                "```\n"
                "uv run mcp-uofx-login\n"
                "```\n"
                "登入完成後，直接重新執行您原本的操作即可（無需重啟 MCP Server）。"
            )

        # 驗證通過，執行實際的 Tool
        return func(*args, **kwargs)
    return wrapper
