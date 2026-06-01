# Contributing

Thanks for contributing to `mcp-uofx`. This repository accepts issues for bug reports, feature requests, and discussion. Pull requests are accepted only from maintainers or collaborators with direct repository access.

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
- Internal notes, generated reports, and environment-specific data must not be added or published.

## Checks

Run the lightweight checks before proposing a change in an issue:

```bash
uv run python tests/test_imports.py
uv run python -m compileall src tests
```

Manual integration scripts may mutate remote state, send notifications, or create records. Review each script before running it.

## Contribution Policy

- Open an issue before proposing behavior, API, documentation, or packaging changes.
- Pull requests from users without direct repository access are closed automatically.
- Keep proposed changes focused and minimal.
- Include sanitized examples, logs, or reproduction steps when relevant.
- Prefer environment variables over hardcoded users, departments, forms, URLs, or company codes.

## Public Repository Hygiene

Before publishing or merging, scan for accidental environment-specific data:

```bash
git grep -n -I -E 'example-secret|access_token|refresh_token|client_secret'
```

Also review staged files for absolute local paths, internal hostnames, test account names, and generated report output.
