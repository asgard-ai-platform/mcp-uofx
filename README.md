# UOF X MCP Server

Custom MCP server for UOF X Total Solution. It exposes curated tools for BPM, organization lookup, agent delegation, punch records, DMS search, ISO documents, notifications, and questionnaires.

## Structure

```text
.
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .env.example
├── examples/
│   ├── claude_desktop_config.json
│   └── vscode_mcp.json
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   ├── manual-tests.md
│   └── tools.md
├── src/
│   └── mcp_uofx/
│       ├── server.py        # stdio MCP entrypoint
│       ├── sse_server.py    # SSE HTTP entrypoint
│       ├── api_client.py    # UOF X HTTP client
│       ├── auth.py          # OAuth credential management
│       ├── login.py         # OAuth login CLI
│       └── tools/           # MCP tool implementations
└── tests/
    ├── test_imports.py      # local import smoke test
    └── manual/              # integration/manual scripts requiring a UOF X environment
```

## Setup

```bash
uv sync
cp .env.example .env
```

Set the required values in `.env`:

```env
UOFX_BASE_URL=https://your-uofx-domain.com
UOFX_API_KEY=your_api_key_here
UOFX_CORP_CODE=your_corp_code
UOFX_DEV_MODE=true
```

## Run

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

## Tools

Tool names are registered with the `uofx_custom_` prefix.

| Area | Tools |
|---|---|
| BPM | `get_pending_tasks`, `get_available_forms`, `get_form_fields`, `apply_bpm_form`, `get_task_detail` |
| Organization | `get_all_departments`, `get_my_profile`, `get_dept_manager`, `get_dept_employees` |
| Delegation | `get_my_agent_settings`, `get_agent_forms`, `set_agent_user`, `set_agent_time`, `delete_agent_user`, `delete_agent_time` |
| Punch | `get_my_punch_history`, `get_dept_punch_report` |
| DMS | `list_dms_folders`, `search_dms` |
| Other | `get_iso_documents`, `send_notification`, `get_pending_questionnaires`, `login` |

See [docs/tools.md](docs/tools.md) for a public tool reference.

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Manual tests](docs/manual-tests.md)
- [Tools](docs/tools.md)

## Tests

Smoke test:

```bash
uv run python tests/test_imports.py
```

Manual integration scripts are under `tests/manual/`. They require a configured `.env` and access to a UOF X environment. Some scripts perform write operations, send notifications, or mutate delegation settings; review them before running.

## Boundaries

- The server operates with the permissions of the configured API key or OAuth user.
- Manual approval steps in UOF X are not bypassed by this server.
- Notification APIs send to one user per request; batch behavior is implemented by looping.
- Some system fields, such as archival widgets, may not be writable through external APIs.

## License

MIT. See [LICENSE](LICENSE).
