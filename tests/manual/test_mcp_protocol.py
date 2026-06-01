"""
MCP Protocol-Level Test (stdio JSON-RPC)

透過 stdio 協議連線 MCP Server，與 VS Code / Claude Desktop 的連線方式完全相同。
Server 以 subprocess 方式啟動，通訊格式為 JSON-RPC over stdin/stdout。

執行方式：
    uv run python tests/manual/test_mcp_protocol.py
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import dotenv_values
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable

# 明確將 .env 讀进來子程序環境（跟 VS Code 的 settings.json env block 行為相同）
_dotenv: dict[str, str] = {k: v for k, v in dotenv_values(ROOT / ".env").items() if v is not None}
ENV: dict[str, str] = {
    **os.environ,
    **_dotenv,
    "PYTHONPATH": str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    # 測試模式強制使用 API Key （跟 VS Code settings.json 的 env.UOFX_DEV_MODE=true 行為相同）
    "UOFX_DEV_MODE": "true",
}

TEST_USER = ENV.get("UOFX_TEST_USER", "test_user")
TEST_AGENT_USER = ENV.get("UOFX_TEST_AGENT_USER", "test_agent_user")
TEST_DEPT_CODE = ENV.get("UOFX_TEST_DEPT_CODE", "TEST_DEPT")
TEST_FORM_CODE = ENV.get("UOFX_TEST_FORM_CODE", "TEST_FORM")
TEST_TASK_ID = ENV.get("UOFX_TEST_TASK_ID", "TEST_TASK_ID")

# ─────────────────────────────────────────────────────────────
# Counter
# ─────────────────────────────────────────────────────────────
results: dict[str, list] = {"pass": [], "bug": [], "fail": []}


def log(name: str, ok: bool, text: str, known_bug: bool = False):
    preview = str(text)[:120].replace("\n", " ")
    if ok:
        results["pass"].append(name)
        print(f"  ✅  {name}")
    elif known_bug:
        results["bug"].append(name)
        print(f"  ⚠️   {name}  (已知 BUG)")
        print(f"       → {preview}")
    else:
        results["fail"].append(name)
        print(f"  ❌  {name}")
        print(f"       → {preview}")


def is_error(text: str) -> bool:
    markers = ("❌", "400 Bad Request", "500 Internal", "Error", "error", "🔒")
    return any(m in text for m in markers)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
async def run():
    params = StdioServerParameters(
        command=PYTHON,
        args=["-m", "mcp_uofx.server"],
        env=ENV,      # 明確傳遞 .env 金鑰（模擬 VS Code settings.json env block）
        cwd=str(ROOT),
    )

    print()
    print("═" * 64)
    print("  UOF X MCP Server — Protocol-Level Test")
    print("  連線方式：stdio JSON-RPC（與 VS Code / Claude Desktop 相同）")
    print("  Server  ：python -m mcp_uofx.server")
    print("═" * 64)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ── 列出所有工具 ──────────────────────────────────
            tools_res = await session.list_tools()
            tool_names = sorted(t.name for t in tools_res.tools)
            print(f"\n🔧 已載入 {len(tool_names)} 個工具：")
            for n in tool_names:
                print(f"   • {n}")

            # ── Phase 1: 組織架構 ─────────────────────────────
            print("\n──── Phase 1  組織架構 ──────────────────────────────")

            r = await session.call_tool("uofx_custom_get_all_departments", {})
            t = r.content[0].text if r.content else ""
            log("get_all_departments", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_my_profile",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_my_profile ({TEST_USER})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_dept_manager",
                                        {"dept_code": TEST_DEPT_CODE})
            t = r.content[0].text if r.content else ""
            log(f"get_dept_manager ({TEST_DEPT_CODE})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_dept_employees",
                                        {"dept_code": TEST_DEPT_CODE})
            t = r.content[0].text if r.content else ""
            log(f"get_dept_employees ({TEST_DEPT_CODE})", not is_error(t), t)

            # ── Phase 2: BPM 表單 ─────────────────────────────
            print("\n──── Phase 2  BPM 表單 ──────────────────────────────")

            r = await session.call_tool("uofx_custom_get_pending_tasks",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_pending_tasks ({TEST_USER})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_available_forms",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_available_forms ({TEST_USER})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_form_fields",
                                        {"form_code_or_id": TEST_FORM_CODE})
            t = r.content[0].text if r.content else ""
            log(f"get_form_fields ({TEST_FORM_CODE})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_apply_bpm_form", {
                "form_id": TEST_FORM_CODE,
                "applicant_code": TEST_USER,
                "applicant_dept_code": TEST_DEPT_CODE,
                "fields": []
            })
            t = r.content[0].text if r.content else ""
            log(f"apply_bpm_form ({TEST_FORM_CODE})", not is_error(t), t, known_bug=True)

            r = await session.call_tool("uofx_custom_get_task_detail",
                                        {"task_id": TEST_TASK_ID})
            t = r.content[0].text if r.content else ""
            log(f"get_task_detail ({TEST_TASK_ID})", not is_error(t), t, known_bug=True)

            # ── Phase 3: 出勤管理 ─────────────────────────────
            print("\n──── Phase 3  出勤管理 ──────────────────────────────")

            r = await session.call_tool("uofx_custom_get_my_punch_history", {
                "user_code": TEST_USER,
                "start_date": "2026-04-28",
                "end_date": "2026-05-28",
            })
            t = r.content[0].text if r.content else ""
            log(f"get_my_punch_history ({TEST_USER})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_dept_punch_report", {
                "dept_code": TEST_DEPT_CODE,
                "start_date": "2026-04-28",
                "end_date": "2026-05-28",
            })
            t = r.content[0].text if r.content else ""
            log(f"get_dept_punch_report ({TEST_DEPT_CODE})", not is_error(t), t)

            # ── Phase 4: 代理人設定 ───────────────────────────
            print("\n──── Phase 4  代理人設定 ────────────────────────────")

            # 4-1: 查詢目前設定（取得 ID）
            r = await session.call_tool("uofx_custom_get_my_agent_settings",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_my_agent_settings ({TEST_USER})", not is_error(t), t)

            # 4-2: 查詢可代理表單清單
            r = await session.call_tool("uofx_custom_get_agent_forms",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_agent_forms ({TEST_USER})", not is_error(t), t)

            # 4-3: 清除現有代理時間（從 settings 取得 ID，用帶括號的分隔符避開標題）
            import re as _re
            settings_r = await session.call_tool("uofx_custom_get_my_agent_settings",
                                                 {"user_code": TEST_USER})
            settings_text = settings_r.content[0].text if settings_r.content else ""
            # 「代理人設定（」帶括號，不會匹配到標題「... 的代理人設定：」
            if "代理人設定（" in settings_text:
                time_section = settings_text[:settings_text.index("代理人設定（")]
            else:
                time_section = settings_text
            existing_time_ids = _re.findall(r'\[ID: ([0-9a-f-]{36})\]', time_section)
            cleaned_ok = True
            for tid in existing_time_ids:
                r = await session.call_tool("uofx_custom_delete_agent_time",
                                            {"user_code": TEST_USER, "time_id": tid})
                t = r.content[0].text if r.content else ""
                if is_error(t):
                    cleaned_ok = False
            log(f"delete_agent_time × {len(existing_time_ids)} 筆", cleaned_ok, f"清除 {len(existing_time_ids)} 筆舊代理時間")

            # 4-4: 新增代理時間（使用未來且不重疊的日期）
            r = await session.call_tool("uofx_custom_set_agent_time", {
                "user_code": TEST_USER,
                "start_time": "2026-07-07T00:00:00+08:00",
                "end_time": "2026-07-09T23:59:59+08:00",
            })
            t = r.content[0].text if r.content else ""
            log(f"set_agent_time ({TEST_USER}, 2026-07-07~09)", not is_error(t), t)

            # 4-5: 清除現有代理人（同樣用帶括號分隔符，避免標題干擾）
            settings_r2 = await session.call_tool("uofx_custom_get_my_agent_settings",
                                                  {"user_code": TEST_USER})
            st2 = settings_r2.content[0].text if settings_r2.content else ""
            if "代理人設定（" in st2:
                user_section = st2[st2.index("代理人設定（"):]
                existing_user_ids = _re.findall(r'\[ID: ([0-9a-f-]{36})\]', user_section)
            else:
                existing_user_ids = []
            cleaned_u_ok = True
            for uid in existing_user_ids:
                r = await session.call_tool("uofx_custom_delete_agent_user",
                                            {"user_code": TEST_USER, "agent_id": uid})
                t = r.content[0].text if r.content else ""
                if is_error(t):
                    cleaned_u_ok = False
            log(f"delete_agent_user × {len(existing_user_ids)} 筆", cleaned_u_ok, f"清除 {len(existing_user_ids)} 筆舊代理人")

            r = await session.call_tool("uofx_custom_set_agent_user", {
                "user_code": TEST_USER,
                "agent_user_code": TEST_AGENT_USER,
            })
            t = r.content[0].text if r.content else ""
            log(f"set_agent_user ({TEST_USER} → {TEST_AGENT_USER})", not is_error(t), t)

            # 4-7: 驗證最終狀態（各有 1 筆，用筆數而非日期字串，避開 UTC 格式問題）
            r = await session.call_tool("uofx_custom_get_my_agent_settings",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            final_ok = (TEST_AGENT_USER in t and
                        "代理時間（共 1 筆）" in t and
                        "代理人設定（共 1 筆）" in t)
            log("verify_agent_settings (1 time + 1 user)", final_ok, t)

            # ── Phase 5: DMS 文件庫 ───────────────────────────
            print("\n──── Phase 5  DMS 文件庫 ────────────────────────────")

            r = await session.call_tool("uofx_custom_list_dms_folders", {})
            t = r.content[0].text if r.content else ""
            log("list_dms_folders", not is_error(t), t)

            r = await session.call_tool("uofx_custom_search_dms",
                                        {"keyword": "請假"})
            t = r.content[0].text if r.content else ""
            log("search_dms (關鍵字：請假)", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_iso_documents", {})
            t = r.content[0].text if r.content else ""
            log("get_iso_documents", not is_error(t), t)

            # ── Phase 6: 通知 & 問卷 ─────────────────────────
            print("\n──── Phase 6  通知 & 問卷 ───────────────────────────")

            r = await session.call_tool("uofx_custom_send_notification", {
                "content": "MCP Protocol Test 通知",
                "user_codes": [TEST_USER],
                "title": "Test",
            })
            t = r.content[0].text if r.content else ""
            log(f"send_notification ({TEST_USER})", not is_error(t), t)

            r = await session.call_tool("uofx_custom_get_pending_questionnaires",
                                        {"user_code": TEST_USER})
            t = r.content[0].text if r.content else ""
            log(f"get_pending_questionnaires ({TEST_USER})", not is_error(t), t)

    # ── 統計 ──────────────────────────────────────────────────
    total = sum(len(v) for v in results.values())
    print()
    print("═" * 64)
    print(f"  總測試數        ：{total}")
    print(f"  ✅ 通過         ：{len(results['pass'])}")
    print(f"  ⚠️  已知BUG（預期）：{len(results['bug'])}")
    print(f"  ❌ 非預期失敗   ：{len(results['fail'])}")
    print("═" * 64)
    print()

    return len(results["fail"]) == 0


if __name__ == "__main__":
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
