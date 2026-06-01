# Configuration

This server can authenticate to UOF X with either API key mode or OAuth mode.

## Environment Variables

| Variable | Required | Description |
|---|---:|---|
| `UOFX_BASE_URL` | Yes | Base URL of your UOF X instance. |
| `UOFX_API_KEY` | API key mode | API key created in UOF X. |
| `UOFX_CORP_CODE` | API key mode | Company code sent with API key requests. |
| `UOFX_DEV_MODE` | No | `true` uses API key mode. `false` uses OAuth credentials when available. |
| `UOFX_VERIFY_SSL` | No | `true` enables strict SSL verification. Defaults to `true`; use `false` only for local or self-signed-certificate test environments. |
| `OAUTH_CLIENT_ID` | OAuth mode | OAuth client ID. |
| `OAUTH_CLIENT_SECRET` | OAuth mode | OAuth client secret. |
| `MCP_SSE_HOST` | SSE mode | Host for the SSE server. |
| `MCP_SSE_PORT` | SSE mode | Port for the SSE server. |
| `MCP_SSE_TEST_TOKEN` | SSE demo | Local test token for the demo SSE middleware. |
| `MCP_SSE_TEST_USER` | SSE demo | User code returned by the demo SSE middleware. |

## API Key Mode

```env
UOFX_DEV_MODE=true
UOFX_BASE_URL=https://your-uofx-domain.com
UOFX_API_KEY=your_api_key_here
UOFX_CORP_CODE=your_corp_code
```

Start the stdio server:

```bash
uv run mcp-uofx
```

## OAuth Mode

```env
UOFX_DEV_MODE=false
UOFX_BASE_URL=https://your-uofx-domain.com
OAUTH_CLIENT_ID=your_oauth_client_id
OAUTH_CLIENT_SECRET=your_oauth_client_secret
```

Log in:

```bash
uv run mcp-uofx-login
```

The login helper stores credentials locally at `~/.uofx/credentials.json`. The MCP server reads that file at tool-call time, so a server restart is not required after login.

## SSE Mode

```env
MCP_SSE_HOST=127.0.0.1
MCP_SSE_PORT=8000
MCP_SSE_TEST_TOKEN=test_token
MCP_SSE_TEST_USER=test_user
```

Start SSE mode:

```bash
uv run mcp-uofx-sse
```

The built-in SSE middleware is intentionally minimal and intended for local testing. Replace it with real bearer token or JWT validation before public deployment.
