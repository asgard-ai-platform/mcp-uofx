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

Once the MCP server is running and connected to your AI assistant, you can interact with UOF X using natural language.

### Check Pending Tasks

**You:** "Show my pending approval tasks."

**AI:** I found your pending UOF X approval tasks and summarized the task titles, form names, applicants, and available links based on your configured permissions.

---

### Search Documents

**You:** "Search DMS for documents related to the onboarding policy."

**AI:** I searched the configured UOF X DMS folders and returned matching documents with metadata that your account is allowed to access.

---

### Inspect Organization Data

**You:** "Find the manager and employees for department SALES."

**AI:** I queried UOF X organization APIs and returned the department manager plus the department employee list, scoped to the configured API key or OAuth user.

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
