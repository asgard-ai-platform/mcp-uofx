# Tools

All registered tool names use the `uofx_custom_` prefix.

## BPM

| Tool | Purpose |
|---|---|
| `uofx_custom_get_pending_tasks` | Query pending BPM tasks for a user. |
| `uofx_custom_get_available_forms` | Query forms the user can start. |
| `uofx_custom_get_form_fields` | Query field metadata required to start a form. |
| `uofx_custom_apply_bpm_form` | Start a BPM form with provided field values. |
| `uofx_custom_get_task_detail` | Query form or task details. |

## Organization

| Tool | Purpose |
|---|---|
| `uofx_custom_get_all_departments` | List departments. |
| `uofx_custom_get_my_profile` | Query user identity, departments, and job information. |
| `uofx_custom_get_dept_manager` | Query a department manager. |
| `uofx_custom_get_dept_employees` | Query employees in a department. |

## Delegation

| Tool | Purpose |
|---|---|
| `uofx_custom_get_my_agent_settings` | Query delegation settings, including IDs for deletion. |
| `uofx_custom_get_agent_forms` | Query forms that can be delegated. |
| `uofx_custom_set_agent_user` | Add a delegate user. |
| `uofx_custom_set_agent_time` | Add a delegation time range. |
| `uofx_custom_delete_agent_user` | Remove a delegate user setting. |
| `uofx_custom_delete_agent_time` | Remove a delegation time range. |

## Punch

| Tool | Purpose |
|---|---|
| `uofx_custom_get_my_punch_history` | Query and summarize a user's punch records. |
| `uofx_custom_get_dept_punch_report` | Query department punch records and detect likely missing punches. |

## DMS And ISO

| Tool | Purpose |
|---|---|
| `uofx_custom_list_dms_folders` | Browse DMS folder roots and children. |
| `uofx_custom_search_dms` | Search DMS documents. |
| `uofx_custom_get_iso_documents` | Search ISO controlled documents. |

## Notifications And Questionnaires

| Tool | Purpose |
|---|---|
| `uofx_custom_send_notification` | Send system notifications to one or more users by looping over the single-recipient API. |
| `uofx_custom_get_pending_questionnaires` | Query questionnaires for a user when supported by the target API configuration. |

## Authentication Helper

| Tool | Purpose |
|---|---|
| `uofx_custom_login` | Return instructions for completing OAuth login with `mcp-uofx-login`. |

## Boundaries

- Some UOF X workflow steps are intentionally restricted by the platform and cannot be bypassed by an MCP tool.
- Some form components may be system-managed and unavailable to external APIs.
- Write-capable tools should be used with the same care as direct API calls.
