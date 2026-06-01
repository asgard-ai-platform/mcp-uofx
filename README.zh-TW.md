# MCP UOF X

[![CI](https://github.com/asgard-ai-platform/mcp-uofx/actions/workflows/ci.yml/badge.svg)](https://github.com/asgard-ai-platform/mcp-uofx/actions/workflows/ci.yml)
[![GitHub tag](https://img.shields.io/github/v/tag/asgard-ai-platform/mcp-uofx)](https://github.com/asgard-ai-platform/mcp-uofx/tags)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io/)

UOF X Total Solution 的 Model Context Protocol 伺服器。它將精選 UOF X API 包裝成 AI 可呼叫的工具，涵蓋 BPM、組織查詢、代理人設定、打卡紀錄、DMS 搜尋、ISO 文件、通知與問卷。

[English](README.md)

本專案是 [Asgard AI Platform](https://github.com/asgard-ai-platform) 開源生態系的一部分。

## 功能特色

- **23 個 MCP 工具**，涵蓋流程、組織、文件、通知、問卷與出勤情境
- **API Key 與 OAuth 兩種模式**，支援服務層級與使用者層級整合
- **stdio 與 SSE 傳輸模式**，可用於本機 MCP client 與 HTTP 型整合
- **Public-safe 設定方式**，透過環境變數與 `.env.example` 管理設定

## 工具

所有工具名稱都使用 `uofx_custom_` 前綴註冊。

| 類別 | 工具 |
|------|------|
| BPM | `get_pending_tasks`, `get_available_forms`, `get_form_fields`, `apply_bpm_form`, `get_task_detail` |
| 組織 | `get_all_departments`, `get_my_profile`, `get_dept_manager`, `get_dept_employees` |
| 代理人 | `get_my_agent_settings`, `get_agent_forms`, `set_agent_user`, `set_agent_time`, `delete_agent_user`, `delete_agent_time` |
| 打卡 | `get_my_punch_history`, `get_dept_punch_report` |
| DMS | `list_dms_folders`, `search_dms` |
| 其他 | `get_iso_documents`, `send_notification`, `get_pending_questionnaires`, `login` |

完整公開工具說明請參考 [docs/tools.md](docs/tools.md)。

## 快速開始

### Clone 並安裝

```bash
git clone https://github.com/asgard-ai-platform/mcp-uofx.git
cd mcp-uofx
uv sync
```

### 設定

```bash
cp .env.example .env
# 編輯 .env，填入你的 UOF X 憑證與服務網址
```

環境變數：

| 變數 | 說明 |
|------|------|
| `UOFX_BASE_URL` | UOF X instance 的 base URL |
| `UOFX_API_KEY` | API Key 模式使用的 API key |
| `UOFX_CORP_CODE` | API Key request 使用的公司代碼 |
| `UOFX_DEV_MODE` | `true` 使用 API Key 模式；`false` 則在可用時使用 OAuth credentials |
| `UOFX_VERIFY_SSL` | `true` 啟用嚴格 SSL 驗證 |
| `OAUTH_CLIENT_ID` | OAuth 模式使用的 client ID |
| `OAUTH_CLIENT_SECRET` | OAuth 模式使用的 client secret |
| `MCP_SSE_HOST` | SSE server host |
| `MCP_SSE_PORT` | SSE server port |

詳細設定請參考 [docs/configuration.md](docs/configuration.md)。

### 執行

Stdio 模式：

```bash
uv run mcp-uofx
```

SSE 模式：

```bash
uv run mcp-uofx-sse
```

OAuth 登入工具：

```bash
uv run mcp-uofx-login
uv run mcp-uofx-login --status
uv run mcp-uofx-login --logout
```

### Claude Desktop 整合

設定範例：

```json
{
  "mcpServers": {
    "uofx": {
      "command": "uv",
      "args": ["run", "mcp-uofx"],
      "cwd": "/path/to/mcp-uofx"
    }
  }
}
```

更多範例請參考 [examples/](examples/)。

## 使用範例

當 MCP server 啟動並連接到 AI assistant 後，你可以用自然語言操作 UOF X。

### 查詢待簽核工作

**你：**「幫我查目前待簽核的工作。」

**AI：** 我已依照目前設定的權限查詢 UOF X 待簽核項目，並整理任務標題、表單名稱、申請人與可用連結。

---

### 搜尋文件

**你：**「幫我在 DMS 搜尋跟 onboarding policy 有關的文件。」

**AI：** 我已搜尋目前帳號可存取的 UOF X DMS 資料夾，並回傳符合條件的文件與 metadata。

---

### 查詢組織資料

**你：**「幫我查 SALES 部門的主管與員工名單。」

**AI：** 我已透過 UOF X 組織 API 查詢部門主管與員工清單，結果會依照目前 API key 或 OAuth 使用者權限回傳。

## 專案結構

```text
mcp-uofx/
├── pyproject.toml              # Package metadata, scripts, and build config
├── uv.lock                     # Locked dependency graph
├── .env.example                # Public environment variable template
├── examples/                   # MCP client configuration examples
├── docs/                       # Public documentation
├── src/mcp_uofx/
│   ├── server.py               # stdio MCP entrypoint
│   ├── sse_server.py           # SSE HTTP entrypoint
│   ├── api_client.py           # UOF X HTTP client
│   ├── auth.py                 # OAuth credential management
│   ├── login.py                # OAuth login CLI
│   └── tools/                  # MCP tool implementations
└── tests/
    ├── test_imports.py         # Public import smoke test
    └── manual/                 # Manual integration scripts requiring UOF X access
```

## 測試

```bash
# 執行公開 smoke test
uv run python tests/test_imports.py

# 編譯 source 與 tests
uv run python -m compileall src tests

# 建置 source distribution 與 wheel
uv build
```

Manual integration scripts 位於 [tests/manual/](tests/manual/)。這些腳本需要已設定的 `.env` 與可存取的 UOF X 環境。部分腳本會執行寫入、發送通知或修改代理人設定，執行前請先逐一檢查。

## 文件

- [架構](docs/architecture.md)
- [設定](docs/configuration.md)
- [Manual tests](docs/manual-tests.md)
- [工具](docs/tools.md)

## 邊界

- Server 會以設定的 API key 或 OAuth 使用者權限執行。
- UOF X 內的人工簽核步驟不會被此 server 繞過。
- 通知 API 每次 request 只發送給一位使用者；批次行為由迴圈實作。
- 部分系統欄位，例如歸檔 widget，可能無法透過外部 API 寫入。

## 授權

MIT License，詳見 [LICENSE](LICENSE)。

## Asgard Ecosystem

本專案是 [Asgard AI Platform](https://github.com/asgard-ai-platform) 的一部分，透過 MCP 讓 AI assistant 能與真實企業與流程系統整合。
