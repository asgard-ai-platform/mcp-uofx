# Architecture

`mcp-uofx` is a Python MCP server built around a small HTTP client and curated tool functions.

## Runtime Flow

```text
MCP client
  -> mcp_uofx.server FastMCP tools
  -> mcp_uofx.tools.* functions
  -> mcp_uofx.api_client.UofXApiClient
  -> UOF X OpenAPI
```

## Entrypoints

| Command | Module | Purpose |
|---|---|---|
| `uv run mcp-uofx` | `mcp_uofx.server` | stdio MCP server. |
| `uv run mcp-uofx-sse` | `mcp_uofx.sse_server` | SSE HTTP server. |
| `uv run mcp-uofx-login` | `mcp_uofx.login` | OAuth login helper. |

## Authentication

In API key mode, requests include `Api-Key` and `CorpCode` headers.

In OAuth mode, the server reads `~/.uofx/credentials.json` on each tool call and sends an `Authorization: Bearer ...` header when a valid token exists.

## Tool Design

Tools are intentionally not a one-to-one mirror of every API endpoint. Some tools combine multiple UOF X calls or add small business-safe transformations so the MCP client receives a more useful result.

## Package Layout

```text
src/mcp_uofx/
├── api_client.py
├── auth.py
├── login.py
├── server.py
├── sse_server.py
└── tools/
```
