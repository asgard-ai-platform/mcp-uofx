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

以下是實際與 UOF X 測試環境（demox3.edetw.com）對話的測試紀錄，展示 MCP server 如何讓 AI 以自然語言完成跨模組業務操作。

---

### 情境一：出勤缺刷偵測

UOF X 打卡報表 API 只回傳有打卡記錄的人。當天完全未打卡的員工，在 API 回傳結果裡不是空值，而是根本不存在。

**情境**：部門主管想確認開發組這個月有沒有人忘記打卡。

```
使用者：開發組五月份有人缺刷嗎？

AI：⚠️ 部門 DEPT_IT_DEV 疑似缺刷 125 筆：
    - it_dev_01 - 開發工程師 - 林前端 (2026-05-01): 未打卡 (0 次)
    - it_dev_01 - 開發工程師 - 林前端 (2026-05-02): 未打卡 (0 次)
    - it_dev_02 - 開發工程師 - 黃後端 (2026-05-01): 未打卡 (0 次)
    ⋯（共 125 筆，涵蓋全月工作日 × 6 位組員）
```

工具先透過組織 API 取得部門全員名單（6 位），再拉打卡報表做差集——把原廠 API 不會回傳的「完全未打卡」紀錄主動補出來。若直接透傳 API 結果，AI 只看得到有打卡的人，會漏報整批缺刷者。

---

### 情境二：代理人設定

UOF X 代理人 API 限制：新時間段不能與現有設定重疊，否則回傳 400 錯誤。一般使用者不知道要先刪舊設定，直接設定會失敗。

**情境**：主管下週出差三天，想把簽核交給同事代理。

```
使用者：我下週一到三要出差，幫我把簽核代理給黃後端。

AI：⚙️ 查詢現有代理設定... 找到 1 筆舊時段。
    ✅ 已清除舊時間段
    ✅ 已清除舊代理人
    📋 確認可代理表單：事假單、（未命名）⋯
    ✅ 成功將代理人設定為 it_dev_02（黃後端）
    ✅ 成功新增代理時間：2026-06-06 00:00 ～ 2026-06-08 23:59
    ⚙️ 驗證：代理設定已生效。
```

工具描述清楚標注時段不可重疊的限制，AI 讀到這條約束後，自動協調「先查詢 → 刪除舊設定 → 設定新值 → 驗證」的序列。使用者不需要知道 API 有這條限制，也不會看到 400 錯誤。

---

### 情境三：部門廣播通知

「通知某部門所有人」在 API 層需要兩步：先查員工清單，再逐一發送通知。兩個動作跨越不同模組，使用者必須自己協調。

**情境**：IT 組長需要在系統停機前通知部門全員。

```
使用者：通知資訊部全體員工，今晚 10 點停機維護。

AI：部門 DEPT_IT_DEV 共有 6 位員工：
    黃後端 (it_dev_02)、吳全端 (it_dev_03)、蔡測試 (it_dev_04)⋯
    ✅ 成功發送通知給 3 位使用者。
    通知標題：今晚 10 點系統停機維護通知
```

查員工清單與發送通知兩個動作在工具內自動串接。一句話跨越組織架構模組和通知模組完成操作。

---

### 情境四：對話式表單申請

展示 AI 如何處理表單的完整生命週期：從起單、審核到合規檢查。

#### 4-1. 員工起單

**情境**：員工要請半天假，用一句話表達需求。

```
使用者：我要請今天下午的事假。

AI：📋 查詢可申請表單... 找到：事假單 (代碼: DMSGENDOC)
    📝 查詢欄位規格：
       - [C003] 原因 (type: text) (必填)
       - [C006] 文件歸檔 (type: archivist) ⚠️系統元件，略過
    ✅ 成功為 it_dev_01 發起表單 DMSGENDOC
       追蹤 ID: c086e05abbe1814b3e462b46f27c459f
```

#### 4-2. 主管審核與合規檢查

**情境**：主管想批假單，但要求 AI 先確認申請人有沒有設代理人。

```
使用者：有多少待簽的假單？幫我檢查有沒有設代理。

AI：✅ 查詢待簽任務清單
    ✅ 對每位申請人進行代理人狀態交叉檢查
    📋 合規判斷：
       - 已設代理者 → 推薦簽結
       - 未設代理者 → 暫緩，發通知提醒設定
    💡 提供 UOF X 簽核連結供主管直接進入系統操作
```

#### 4-3. 員工補設代理

**情境**：員工收到系統催辦通知後，請 AI 協助設定代理人。

```
使用者：我收到提醒要設代理，幫我設定。

AI：✅ 設定代理人與代理時段
    ✅ 驗證設定已生效
    ✅ 推播通知主管「已完成代理設定，可簽結」
```

表單的完整生命週期涵蓋：查表單 → 查欄位 → 起單 → 合規檢查 → 催辦 → 補設定 → 回報。這些步驟串接了 BPM、代理人、通知三個模組，展示了工具編排的業務價值。

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
