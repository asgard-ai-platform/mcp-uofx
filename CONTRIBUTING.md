# Contributing

Thanks for contributing to `mcp-uofx`.

## Development Setup

```bash
uv sync
cp .env.example .env
```

Use environment variables or `.env` for local credentials. Do not commit real credentials, access tokens, user data, internal hostnames, generated reports, or IDE metadata.

## Project Layout

- `src/mcp_uofx/` contains the MCP server and tool implementations.
- `tests/test_imports.py` is the public smoke test.
- `tests/manual/` contains integration scripts that require a real UOF X environment.
- `docs/` contains public documentation.
- `docs/internal/` is ignored and must not be published.

## Checks

Run the lightweight checks before opening a pull request:

```bash
uv run python tests/test_imports.py
uv run python -m compileall src tests
```

Manual integration scripts may mutate remote state, send notifications, or create records. Review each script before running it.

## Pull Request Guidelines

- Keep changes focused and minimal.
- Update README or docs when behavior, setup, tool names, or commands change.
- Prefer environment variables over hardcoded users, departments, forms, URLs, or company codes.
- Avoid adding generated reports or local IDE files.

## Public Repository Hygiene

Before publishing or merging, scan for accidental environment-specific data:

```bash
git grep -n -I -E 'example-secret|access_token|refresh_token|client_secret'
```

Also review staged files for absolute local paths, internal hostnames, test account names, and generated report output.
