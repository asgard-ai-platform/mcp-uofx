# Manual Tests

Manual integration scripts live in `tests/manual/`. They are not intended for automated CI by default.

## Requirements

- A configured `.env` file.
- Network access to a UOF X environment.
- Test users, departments, forms, and task IDs prepared in that environment.

Optional fixture variables:

```env
UOFX_TEST_USER=test_user
UOFX_TEST_AGENT_USER=test_agent_user
UOFX_TEST_DEPT_CODE=TEST_DEPT
UOFX_TEST_FORM_CODE=TEST_FORM
UOFX_TEST_FORM_FIELD_ID=TEST_FIELD_ID
UOFX_TEST_TASK_ID=TEST_TASK_ID
```

## Smoke Test

This test does not call UOF X APIs:

```bash
uv run python tests/test_imports.py
```

## Protocol Test

```bash
uv run python tests/manual/test_mcp_protocol.py
```

This starts the MCP server through stdio and calls tools through the MCP protocol.

## Scenario Test

```bash
uv run python tests/manual/test_innovative_scenarios.py
```

This exercises multi-step tool flows and may mutate delegation settings or send notifications depending on the configured test fixtures.

## Raw API And Verification Scripts

Scripts named `verify_*.py` and `test_raw_apis.py` are exploratory integration checks. Review them before running because some perform write operations or generate local reports.

Generated reports are ignored by `.gitignore`.
