import os
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

def _load_env_file(path: Path) -> None:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())


# 讀取 repo root 或目前工作目錄的 .env；正式部署建議直接使用環境變數。
for env_path in (Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"):
    _load_env_file(env_path)

class UofXApiClient:
    def __init__(self):
        # 讀取環境變數（必須在 .env 或執行環境中設置）
        self.base_url = os.getenv("UOFX_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("UOFX_API_KEY", "")
        self.corp_code = os.getenv("UOFX_CORP_CODE", "")
        
        self.headers = {
            "Api-Key": self.api_key,
            "CorpCode": self.corp_code,
            "Content-Type": "application/json"
        }

    def _get_client(self) -> httpx.Client:
        # 動態載入 auth，避免循環依賴
        from .auth import get_access_token
        
        headers = self.headers.copy()
        
        # DEV_MODE=true 時強制使用 API Key，完全略過 OAuth credentials
        # 避免殘留的舊 token（scope 可能不足）覆蓋 API Key 導致 401
        dev_mode = os.getenv("UOFX_DEV_MODE", "false").lower() == "true"
        if not dev_mode:
            # 熱讀取 ~/.uofx/credentials.json，若有有效 Token 則優先使用
            access_token = get_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
                headers.pop("Api-Key", None)
        
        # 預設啟用 SSL 驗證；只有在本機或自簽憑證測試環境才建議明確關閉。
        verify_ssl = os.getenv("UOFX_VERIFY_SSL", "true").lower() == "true"
        return httpx.Client(headers=headers, verify=verify_ssl, timeout=30.0)

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise RuntimeError("UOFX_BASE_URL is required. Set it in .env or environment variables.")
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """封裝 GET 請求"""
        url = self._build_url(path)
        with self._get_client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def post(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """封裝 POST 請求"""
        url = self._build_url(path)
        with self._get_client() as client:
            response = client.post(url, json=payload or {})
            response.raise_for_status()
            return response.json()

    def delete(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """封裝 DELETE 請求（帶 JSON body）"""
        url = self._build_url(path)
        with self._get_client() as client:
            response = client.request("DELETE", url, json=payload or {})
            response.raise_for_status()
            # DELETE 可能回傳空 body
            return response.json() if response.content else {}

# 全域單一實例，方便 Tools 調用
uofx_client = UofXApiClient()
