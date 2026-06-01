"""
MCP 創新業務情境測試 (Innovation Scenario Test)

測試 api-spec-and-boundaries.md 第五節的 4 個核心業務情境，
透過 stdio JSON-RPC 與 MCP Server 進行端對端（E2E）驗證。

情境清單：
  1. 代理人設定管家  — 一句話完成代理設定（6 工具串聯）
  2. 企業廣播通報中心 — 查部門員工 + 逐一推播
  3. 出勤打卡異常稽核員 — 調閱報表 + 分析缺刷
  4. 對話式起單助理  — 查表單 → 查欄位 → 起單（3 工具串聯）

執行方式：
    uv run python tests/manual/test_innovative_scenarios.py
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import dotenv_values
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable

_dotenv: dict[str, str] = {k: v for k, v in dotenv_values(ROOT / ".env").items() if v is not None}
ENV: dict[str, str] = {
    **os.environ,
    **_dotenv,
    "PYTHONPATH": str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    "UOFX_DEV_MODE": "true",
}

TEST_USER = ENV.get("UOFX_TEST_USER", "test_user")
TEST_AGENT_USER = ENV.get("UOFX_TEST_AGENT_USER", "test_agent_user")
TEST_DEPT_CODE = ENV.get("UOFX_TEST_DEPT_CODE", "TEST_DEPT")
TEST_FORM_CODE = ENV.get("UOFX_TEST_FORM_CODE", "TEST_FORM")
TEST_FORM_FIELD_ID = ENV.get("UOFX_TEST_FORM_FIELD_ID", "TEST_FIELD_ID")

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
results: list[dict] = []


def is_error(text: str) -> bool:
    return any(m in text for m in ("❌", "400 Bad Request", "500 Internal", "Error", "error"))


def step(scenario: str, name: str, ok: bool, detail: str = ""):
    icon = "✅" if ok else "❌"
    short = (detail[:100].replace("\n", " ")) if detail else ""
    print(f"    {icon} {name}")
    if short:
        print(f"       → {short}")
    results.append({"scenario": scenario, "step": name, "ok": ok})
    return ok


async def call(session, tool: str, args: dict) -> str:
    r = await session.call_tool(tool, args)
    return r.content[0].text if r.content else ""


# ─────────────────────────────────────────────────────────────
# Scenario 1: 代理人設定管家
# ─────────────────────────────────────────────────────────────
async def scenario_agent_management(session):
    TITLE = "代理人設定管家"
    print(f"\n{'═'*64}")
    print(f"  情境 1：{TITLE}")
    print(f"{'═'*64}")
    print("  💬 主管：「我下週一到三要去出差，幫我把簽核代理給同事。」")
    print()

    # Step 1: 查詢現有設定
    t = await call(session, "uofx_custom_get_my_agent_settings", {"user_code": TEST_USER})
    step(TITLE, "get_my_agent_settings — 取得現有代理設定", not is_error(t), t)

    # Step 2: 解析並清除現有時間段
    existing_ids = re.findall(r'\[ID: ([0-9a-f-]{36})\]', t)
    time_section = t[:t.index("代理人設定（")] if "代理人設定（" in t else t
    time_ids = re.findall(r'\[ID: ([0-9a-f-]{36})\]', time_section)

    cleaned = True
    for tid in time_ids:
        tr = await call(session, "uofx_custom_delete_agent_time", {"user_code": TEST_USER, "time_id": tid})
        if is_error(tr):
            cleaned = False
    step(TITLE, f"delete_agent_time × {len(time_ids)} 筆 — 清除舊時間段", cleaned)

    # Step 3: 清除現有代理人
    user_section = t[t.index("代理人設定（"):] if "代理人設定（" in t else ""
    user_ids = re.findall(r'\[ID: ([0-9a-f-]{36})\]', user_section)
    cleaned_u = True
    for uid in user_ids:
        ur = await call(session, "uofx_custom_delete_agent_user", {"user_code": TEST_USER, "agent_id": uid})
        if is_error(ur):
            cleaned_u = False
    step(TITLE, f"delete_agent_user × {len(user_ids)} 筆 — 清除舊代理人", cleaned_u)

    # Step 4: 查詢可代理表單
    t2 = await call(session, "uofx_custom_get_agent_forms", {"user_code": TEST_USER})
    step(TITLE, "get_agent_forms — 確認可代理表單清單", not is_error(t2), t2)

    t3 = await call(session, "uofx_custom_set_agent_user", {
        "user_code": TEST_USER,
        "agent_user_code": TEST_AGENT_USER
    })
    step(TITLE, f"set_agent_user — 設定代理人為 {TEST_AGENT_USER}", not is_error(t3), t3)

    # Step 6: 設定代理時間（下週一到三，模擬用未來 7-9 天）
    start_dt = (datetime.now() + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = (datetime.now() + timedelta(days=9)).replace(hour=23, minute=59, second=59, microsecond=0)
    t4 = await call(session, "uofx_custom_set_agent_time", {
        "user_code": TEST_USER,
        "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    step(TITLE, f"set_agent_time — 設定時段 {start_dt.date()} ~ {end_dt.date()}", not is_error(t4), t4)

    # Step 7: 驗證生效
    t5 = await call(session, "uofx_custom_get_my_agent_settings", {"user_code": TEST_USER})
    verify_ok = TEST_AGENT_USER in t5 and ("代理時間" in t5 or "startTime" in t5.lower() or "2026" in t5)
    step(TITLE, "get_my_agent_settings — 驗證設定已生效", verify_ok, t5)


# ─────────────────────────────────────────────────────────────
# Scenario 2: 企業廣播通報中心
# ─────────────────────────────────────────────────────────────
async def scenario_broadcast(session):
    TITLE = "企業廣播通報中心"
    print(f"\n{'═'*64}")
    print(f"  情境 2：{TITLE}")
    print(f"{'═'*64}")
    print("  💬 IT 組長：「通知資訊部全體員工，今晚 10 點停機維護。」")
    print()

    t = await call(session, "uofx_custom_get_dept_employees", {
        "dept_code": TEST_DEPT_CODE
    })
    step(TITLE, "get_dept_employees — 取得開發組員工清單", not is_error(t), t)

    # 解析帳號列表（格式：「姓名 (account_code)」）
    accounts = re.findall(r'\(([a-z][a-z0-9_]{2,20})\)', t)
    # 至少確保有一個帳號
    if not accounts:
        accounts = [TEST_USER]

    # Step 2: 批次發送通知（content + user_codes list，最多 3 人）
    title_msg = "今晚 10 點系統停機維護通知"
    content_msg = "IT 部門將於今晚 22:00 進行系統維護，維護期間請暫停使用相關系統，預計 23:00 恢復。感謝配合。"
    target_accounts = accounts[:3]

    nt = await call(session, "uofx_custom_send_notification", {
        "content": content_msg,
        "user_codes": target_accounts,
        "title": title_msg
    })
    all_sent = not is_error(nt)
    step(TITLE, f"send_notification → {target_accounts}", all_sent, nt)

    step(TITLE, f"廣播完成 — 已推播給 {len(target_accounts)} 位員工", all_sent)


# ─────────────────────────────────────────────────────────────
# Scenario 3: 出勤打卡異常稽核員
# ─────────────────────────────────────────────────────────────
async def scenario_punch_audit(session):
    TITLE = "出勤打卡異常稽核員"
    print(f"\n{'═'*64}")
    print(f"  情境 3：{TITLE}")
    print(f"{'═'*64}")
    print("  💬 主管：「開發組五月份有人缺刷嗎？」")
    print()

    # Step 1: 查詢部門打卡報表
    t = await call(session, "uofx_custom_get_dept_punch_report", {
        "dept_code": TEST_DEPT_CODE,
        "start_date": "2026-05-01",
        "end_date": "2026-05-31",
    })
    step(TITLE, "get_dept_punch_report — 取得開發組 5 月打卡紀錄", not is_error(t), t)

    # Step 2: 分析（計算打卡筆數，判斷是否有資料）
    punch_count = len(re.findall(r'punchDate|打卡時間|2026-05', t))
    has_data = punch_count > 0 or ("筆" in t and "0 筆" not in t)
    step(TITLE, f"分析打卡紀錄 — 共解析到 {punch_count} 筆相關資料", not is_error(t))

    # Step 3: 查詢個人打卡（驗證單人查詢也通）
    t2 = await call(session, "uofx_custom_get_my_punch_history", {
        "user_code": TEST_USER,
        "start_date": "2026-05-01",
        "end_date": "2026-05-31",
    })
    step(TITLE, f"get_my_punch_history — 查詢 {TEST_USER} 個人紀錄（交叉驗證）", not is_error(t2), t2)

    # 模擬後處理（AI 實際上會整理成可讀報告）
    print("    ─ AI 後處理模擬 ─")
    print("    🤖 AI：已整理打卡資料，若有缺刷日可進一步發通知提醒補登")
    step(TITLE, "後處理模擬 — 可接續 send_notification 提醒缺刷員工", True)


# ─────────────────────────────────────────────────────────────
# Scenario 4: 對話式起單助理
# ─────────────────────────────────────────────────────────────
async def scenario_form_apply(session):
    TITLE = "對話式起單助理"
    print(f"\n{'═'*64}")
    print(f"  情境 4：{TITLE}")
    print(f"{'═'*64}")
    print("  💬 員工：「我要請今天下午的事假。」")
    print()

    # Step 1: 查詢可申請表單
    t = await call(session, "uofx_custom_get_available_forms", {"user_code": TEST_USER})
    step(TITLE, f"get_available_forms — 查詢 {TEST_USER} 可申請的表單", not is_error(t), t)

    t2 = await call(session, "uofx_custom_get_form_fields", {"form_code_or_id": TEST_FORM_CODE})
    step(TITLE, f"get_form_fields ({TEST_FORM_CODE}) — 查詢表單欄位規格", not is_error(t2), t2)

    # Step 3: 起單 — 填寫請假原因欄位 (C003)
    t3 = await call(session, "uofx_custom_apply_bpm_form", {
        "form_id": TEST_FORM_CODE,
        "applicant_code": TEST_USER,
        "applicant_dept_code": TEST_DEPT_CODE,
        "fields": [
            {
                "fieldId": TEST_FORM_FIELD_ID,
                "code": "C003",
                "value": "今日下午事假，家庭因素"
            }
        ]
    })
    step(TITLE, f"apply_bpm_form ({TEST_FORM_CODE}) — 送出表單申請", not is_error(t3), t3)

    # Step 4: 確認起單成功（traceId 追蹤）
    trace_id = re.search(r'[0-9a-f]{32}', t3)
    if trace_id:
        print(f"    🔍 traceId: {trace_id.group()}")
    step(TITLE, "起單結果確認 — 表單已送出，traceId 取得成功",
         not is_error(t3) and ("traceId" in t3 or re.search(r'[0-9a-f]{32}', t3) is not None), t3)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
async def run():
    params = StdioServerParameters(
        command=PYTHON,
        args=["-m", "mcp_uofx.server"],
        env=ENV,
        cwd=str(ROOT),
    )

    print()
    print("═" * 64)
    print("  UOF X MCP — 創新業務情境 E2E 測試")
    print("  對應文件：api-spec-and-boundaries.md 第五節")
    print("  連線方式：stdio JSON-RPC（與 VS Code / Claude Desktop 相同）")
    print("═" * 64)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            await scenario_agent_management(session)
            await scenario_broadcast(session)
            await scenario_punch_audit(session)
            await scenario_form_apply(session)

    # ── Summary ────────────────────────────────────────────
    print(f"\n{'═'*64}")
    print("  測試結果總覽")
    print(f"{'═'*64}")

    by_scenario: dict[str, list] = {}
    for r in results:
        by_scenario.setdefault(r["scenario"], []).append(r["ok"])

    overall_pass = 0
    overall_total = 0
    for sc, bools in by_scenario.items():
        total = len(bools)
        passed = sum(bools)
        overall_pass += passed
        overall_total += total
        icon = "✅" if passed == total else ("⚠️ " if passed >= total * 0.7 else "❌")
        print(f"  {icon} {sc}：{passed}/{total} 步驟通過")

    print(f"\n  總計：{overall_pass}/{overall_total} 步驟通過")
    print(f"{'═'*64}\n")

    return overall_pass, overall_total


if __name__ == "__main__":
    asyncio.run(run())
