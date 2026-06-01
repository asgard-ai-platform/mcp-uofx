# MCP UOF X

[![CI](https://github.com/asgard-ai-platform/mcp-uofx/actions/workflows/ci.yml/badge.svg)](https://github.com/asgard-ai-platform/mcp-uofx/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/mcp-uofx.svg)](https://pypi.org/project/mcp-uofx/)
[![Python versions](https://img.shields.io/pypi/pyversions/mcp-uofx.svg)](https://pypi.org/project/mcp-uofx/)
[![GitHub tag](https://img.shields.io/github/v/tag/asgard-ai-platform/mcp-uofx)](https://github.com/asgard-ai-platform/mcp-uofx/tags)
[![GitHub stars](https://img.shields.io/github/stars/asgard-ai-platform/mcp-uofx)](https://github.com/asgard-ai-platform/mcp-uofx/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/asgard-ai-platform/mcp-uofx)](https://github.com/asgard-ai-platform/mcp-uofx/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/asgard-ai-platform/mcp-uofx)](https://github.com/asgard-ai-platform/mcp-uofx/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io/)

Model Context Protocol server for UOF X Total Solution. Exposes curated UOF X APIs as AI-callable tools for BPM, organization lookup, agent delegation, punch records, DMS search, ISO documents, notifications, and questionnaires.

[繁體中文](README.zh-TW.md)

Part of the [Asgard AI Platform](https://github.com/asgard-ai-platform) open-source ecosystem.

## What This Does

- **23 MCP tools** covering workflow, organization, document, notification, questionnaire, and attendance use cases
- **API key and OAuth modes** for service-level and user-level integrations
- **stdio and SSE transports** for local MCP clients and HTTP-based integrations
- **Public-safe configuration** through environment variables and `.env.example`

## Tools (23)

Tool names are registered with the `uofx_custom_` prefix.

| Area | Tools |
|------|-------|
| BPM | `get_pending_tasks`, `get_available_forms`, `get_form_fields`, `apply_bpm_form`, `get_task_detail` |
| Organization | `get_all_departments`, `get_my_profile`, `get_dept_manager`, `get_dept_employees` |
| Agent Delegation | `get_my_agent_settings`, `get_agent_forms`, `set_agent_user`, `set_agent_time`, `delete_agent_user`, `delete_agent_time` |
| Punch | `get_my_punch_history`, `get_dept_punch_report` |
| DMS | `list_dms_folders`, `search_dms` |
| Other | `get_iso_documents`, `send_notification`, `get_pending_questionnaires`, `login` |

See [docs/tools.md](docs/tools.md) for the full public tool reference.

## Quick Start

### Install

```bash
pip install mcp-uofx
```

For local development:

```bash
git clone https://github.com/asgard-ai-platform/mcp-uofx.git
cd mcp-uofx
uv sync
```

### Configure

```bash
cp .env.example .env
# Edit .env with your UOF X credentials and service URL
```

Environment variables:

| Variable | Description |
|----------|-------------|
| `UOFX_BASE_URL` | Base URL of your UOF X instance |
| `UOFX_API_KEY` | API key for API key mode |
| `UOFX_CORP_CODE` | Company code sent with API key requests |
| `UOFX_DEV_MODE` | `true` uses API key mode; `false` uses OAuth credentials when available |
| `UOFX_VERIFY_SSL` | `true` enables strict SSL verification |
| `OAUTH_CLIENT_ID` | OAuth client ID for OAuth mode |
| `OAUTH_CLIENT_SECRET` | OAuth client secret for OAuth mode |
| `MCP_SSE_HOST` | Host for the SSE server |
| `MCP_SSE_PORT` | Port for the SSE server |

See [docs/configuration.md](docs/configuration.md) for details.

### Run

Stdio mode:

```bash
uv run mcp-uofx
```

SSE mode:

```bash
uv run mcp-uofx-sse
```

OAuth login helper:

```bash
uv run mcp-uofx-login
uv run mcp-uofx-login --status
uv run mcp-uofx-login --logout
```

### Use with Claude Desktop

Example configuration:

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

More examples are available in [examples/](examples/).

### Use with Claude Code

After installing the package and configuring environment variables, add the stdio MCP server:

```bash
claude mcp add uofx -- mcp-uofx
```

For a local checkout, run it through `uv` from the repository directory:

```bash
claude mcp add uofx -- uv --directory /path/to/mcp-uofx run mcp-uofx
```

## Usage Examples

The following are actual test conversations recorded against the UOF X test environment (demox3.edetw.com).

---

### Scenario 1: Missing Punch Detection

The UOF X punch report API only returns records for employees who did clock in. Employees who never clocked in are absent from the response entirely—not present as null values.

**Context:** A department manager wants to check whether anyone on the dev team forgot to clock in this month.

```
使用者：開發組五月份有人缺刷嗎？

AI：⚠️ 部門 DEPT_IT_DEV 疑似缺刷 125 筆：
    - it_dev_01 - 開發工程師 - 林前端 (2026-05-01): 未打卡 (0 次)
    - it_dev_01 - 開發工程師 - 林前端 (2026-05-02): 未打卡 (0 次)
    - it_dev_02 - 開發工程師 - 黃後端 (2026-05-01): 未打卡 (0 次)
    ⋯（共 125 筆，涵蓋全月工作日 × 6 位組員）
```

The tool fetches the full department roster (6 members) from the organization API, then computes a set difference against the punch report—surfacing completely absent employees that the vendor API would never return. Passing the raw API result to the AI would only show employees who did clock in, silently missing anyone who skipped entirely.

---

### Scenario 2: Agent Delegation

The UOF X delegation API rejects new time slots that overlap with existing ones with a 400 error. Most users don't know to delete old settings first; setting directly will fail.

**Context:** A manager is going on a three-day business trip next week and wants to delegate approvals to a colleague.

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

The no-overlap constraint is documented in the tool description. The AI reads it before making any calls and automatically sequences: query → delete old settings → set new values → verify. The user never sees the 400 error.

---

### Scenario 3: Department Broadcast

Sending a notification to an entire department requires two steps at the API level: fetch the employee list, then send individually. These actions span two separate modules.

**Context:** An IT lead needs to notify the entire department before a scheduled maintenance window.

```
使用者：通知資訊部全體員工，今晚 10 點停機維護。

AI：部門 DEPT_IT_DEV 共有 6 位員工：
    黃後端 (it_dev_02)、吳全端 (it_dev_03)、蔡測試 (it_dev_04)⋯
    ✅ 成功發送通知給 3 位使用者。
    通知標題：今晚 10 點系統停機維護通知
```

Fetching the employee list and dispatching notifications are chained inside the tool. A single sentence spans the organization and notification modules.

---

### Scenario 4: Conversational Form Lifecycle

A full BPM form lifecycle: submission, compliance check, follow-up, and approval.

#### 4-1. Employee Submits Leave

**Context:** An employee wants to take half a day off and expresses it in one sentence.

```
使用者：我要請今天下午的事假。

AI：📋 查詢可申請表單... 找到：事假單 (代碼: DMSGENDOC)
    📝 查詢欄位規格：
       - [C003] 原因 (type: text) (必填)
       - [C006] 文件歸檔 (type: archivist) ⚠️系統元件，略過
    ✅ 成功為 it_dev_01 發起表單 DMSGENDOC
       追蹤 ID: c086e05abbe1814b3e462b46f27c459f
```

#### 4-2. Manager Review with Compliance Check

**Context:** The manager wants to approve leave requests but asks the AI to verify that applicants have set a delegation first.

```
使用者：有多少待簽的假單？幫我檢查有沒有設代理。

AI：✅ 查詢待簽任務清單
    ✅ 對每位申請人進行代理人狀態交叉檢查
    📋 合規判斷：
       - 已設代理者 → 推薦簽結
       - 未設代理者 → 暫緩，發通知提醒設定
    💡 提供 UOF X 簽核連結供主管直接進入系統操作
```

#### 4-3. Employee Sets Delegation

**Context:** An employee receives the follow-up notification and asks the AI to set up delegation.

```
使用者：我收到提醒要設代理，幫我設定。

AI：✅ 設定代理人與代理時段
    ✅ 驗證設定已生效
    ✅ 推播通知主管「已完成代理設定，可簽結」
```

The complete lifecycle spans: list forms → inspect fields → submit → compliance check → follow-up → configure delegation → notify. These steps chain BPM, delegation, and notification modules together.

## Project Structure

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

## Testing

```bash
# Run the public smoke test
uv run python tests/test_imports.py

# Compile source and tests
uv run python -m compileall src tests

# Build source distribution and wheel
uv build
```

Manual integration scripts are under [tests/manual/](tests/manual/). They require a configured `.env` and access to a UOF X environment. Some scripts perform write operations, send notifications, or mutate delegation settings; review them before running.

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Manual tests](docs/manual-tests.md)
- [Tools](docs/tools.md)

## Boundaries

- The server operates with the permissions of the configured API key or OAuth user.
- Manual approval steps in UOF X are not bypassed by this server.
- Notification APIs send to one user per request; batch behavior is implemented by looping.
- Some system fields, such as archival widgets, may not be writable through external APIs.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Part of the Asgard Ecosystem

This server is part of the [Asgard AI Platform](https://github.com/asgard-ai-platform), connecting AI assistants to real-world enterprise and workflow systems through MCP.
