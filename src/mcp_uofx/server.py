from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from pathlib import Path

# 從目前工作目錄或 repo root 載入 .env（不覆寫外部傳入的環境變數）
load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

from .tools.punch import get_my_punch_history, get_dept_punch_report
from .tools.org import get_department_manager, get_department_employees, get_my_profile, get_all_departments
from .tools.bpm import get_pending_bpm_tasks, apply_bpm_form, get_available_forms, get_form_fields, get_task_detail
from .tools.agent import get_my_agent_settings, get_agent_forms, set_agent_time, delete_agent_time, set_agent_user, delete_agent_user
from .tools.dms import search_dms_document, list_dms_folders
from .tools.notification import send_system_notification
from .tools.questionnaire import get_pending_questionnaires
from .tools.iso import get_iso_documents
from .auth import require_auth, read_credentials, CREDENTIALS_FILE


# 建立 FastMCP 伺服器實例
mcp = FastMCP("UOF_X_Total_Solution")


@mcp.tool()
def uofx_custom_login() -> str:
    """
    引導使用者完成 UOF X OAuth 登入。
    當出現權限錯誤時，請呼叫此工具並將登入指引提供給使用者。
    登入完成後，無需重啟 MCP Server，直接重試即可。
    """
    # 先檢查是否已經有有效的 credential（熱讀取）
    creds = read_credentials()
    if creds is not None:
        import time
        ttl = creds.get("expires_at", 0) - time.time()
        return (
            f"✅ 您已經登入！Token 剩餘效期約 {ttl / 60:.0f} 分鐘。\n"
            f"📂 憑證路徑: `{CREDENTIALS_FILE}`\n\n"
            f"如需重新登入，請在終端機執行：\n"
            f"```\nuv run mcp-uofx-login\n```"
        )

    # 尚未登入，引導使用者使用獨立 CLI 登入
    return (
        f"🔐 請使用者在終端機執行以下指令進行登入：\n\n"
        f"```\nuv run mcp-uofx-login\n```\n\n"
        f"登入完成後，**無需重啟 MCP Server**，直接重新執行您的操作即可。\n\n"
        f"其他指令：\n"
        f"- 查看登入狀態: `uv run mcp-uofx-login --status`\n"
        f"- 登出: `uv run mcp-uofx-login --logout`"
    )

@mcp.tool()
@require_auth
def uofx_custom_get_pending_tasks(user_code: str, user_type: int = 0) -> str:
    """查詢使用者的待辦簽核表單"""
    return get_pending_bpm_tasks(user_code, user_type)

@mcp.tool()
@require_auth
def uofx_custom_apply_bpm_form(form_id: str, applicant_code: str, applicant_dept_code: str, fields: list, applicant_type: int = 0) -> str:
    """為主動發起外部表單"""
    return apply_bpm_form(form_id, applicant_code, applicant_dept_code, fields, applicant_type)

@mcp.tool()
@require_auth
def uofx_custom_get_available_forms(user_code: str, user_type: int = 0) -> str:
    """查詢使用者可發起的表單"""
    return get_available_forms(user_code, user_type)

@mcp.tool()
@require_auth
def uofx_custom_get_form_fields(form_code_or_id: str) -> str:
    """查詢起單時所需的欄位格式"""
    return get_form_fields(form_code_or_id)

@mcp.tool()
@require_auth
def uofx_custom_get_task_detail(task_id: str) -> str:
    """查詢單據詳細進度與狀態"""
    return get_task_detail(task_id)

@mcp.tool()
@require_auth
def uofx_custom_get_my_punch_history(user_code: str, start_date: str, end_date: str, user_type: int = 0) -> str:
    """查詢個人出勤紀錄，並指出打卡異常（遲到/早退/未打卡）。日期格式 YYYY-MM-DD"""
    return get_my_punch_history(user_code, start_date, end_date, user_type)

@mcp.tool()
@require_auth
def uofx_custom_get_dept_punch_report(dept_code: str, start_date: str, end_date: str, include_sub: bool = False) -> str:
    """查詢部門人員的異常打卡紀錄。日期格式 YYYY-MM-DD"""
    return get_dept_punch_report(dept_code, start_date, end_date, include_sub)

@mcp.tool()
@require_auth
def uofx_custom_get_dept_manager(dept_code: str) -> str:
    """查詢特定部門的主管資訊"""
    return get_department_manager(dept_code)

@mcp.tool()
@require_auth
def uofx_custom_get_dept_employees(dept_code: str) -> str:
    """查詢特定部門的員工名單"""
    return get_department_employees(dept_code)

@mcp.tool()
@require_auth
def uofx_custom_get_my_profile(user_code: str, user_type: int = 0) -> str:
    """取得使用者的完整身份（姓名、部門、職稱等），所有其他 Tool 的前置必要步驟。user_type: 0 為帳號，1 為員工編號。"""
    return get_my_profile(user_code, user_type)

@mcp.tool()
@require_auth
def uofx_custom_get_all_departments() -> str:
    """取得完整組織架構部門清單"""
    return get_all_departments()

@mcp.tool()
@require_auth
def uofx_custom_get_my_agent_settings(user_code: str, user_type: int = 0) -> str:
    """查詢使用者的代理人設定狀態（含 ID，可用於後續刪除操作）"""
    return get_my_agent_settings(user_code, user_type)

@mcp.tool()
@require_auth
def uofx_custom_get_agent_forms(user_code: str, user_type: int = 0) -> str:
    """查詢使用者可以被代理的表單清單"""
    return get_agent_forms(user_code, user_type)

@mcp.tool()
@require_auth
def uofx_custom_set_agent_time(user_code: str, start_time: str, end_time: str, user_type: int = 0) -> str:
    """新增代理時間段（ISO8601 格式含時區，如 2026-06-22T00:00:00+08:00）。時間段不可重疊，重疊請先刪除舊設定。"""
    return set_agent_time(user_code, start_time, end_time, user_type)

@mcp.tool()
@require_auth
def uofx_custom_delete_agent_time(user_code: str, time_id: str, user_type: int = 0) -> str:
    """刪除指定的代理時間段。time_id 從 get_my_agent_settings 的回傳中取得。"""
    return delete_agent_time(user_code, time_id, user_type)

@mcp.tool()
@require_auth
def uofx_custom_set_agent_user(user_code: str, agent_user_code: str, user_type: int = 0, agent_user_type: int = 0, from_dept_code: str = "") -> str:
    """新增代理人。不填 from_dept_code 表示代理全部部門的表單。"""
    return set_agent_user(user_code, agent_user_code, user_type, agent_user_type, from_dept_code)

@mcp.tool()
@require_auth
def uofx_custom_delete_agent_user(user_code: str, agent_id: str, user_type: int = 0) -> str:
    """刪除指定的代理人設定。agent_id 從 get_my_agent_settings 的回傳中取得。"""
    return delete_agent_user(user_code, agent_id, user_type)

@mcp.tool()
@require_auth
def uofx_custom_search_dms(keyword: str, folder_code: str = None, folder_path: str = None, category: int = 0) -> str:
    """搜尋 DMS 文件庫中的文件。keyword=檔名關鍵字, folder_path=指定搜尋路徑(如'/公司規章/人事管理'), category: 0=全部, 1=草稿, 2=發行, 3=作廢"""
    return search_dms_document(keyword, folder_code, folder_path, category)

@mcp.tool()
@require_auth
def uofx_custom_list_dms_folders(root_code: str = None) -> str:
    """查詢 DMS 文件目錄。不指定 root_code 回傳根目錄；指定的話回傳該目錄底下的子目錄"""
    return list_dms_folders(root_code)

@mcp.tool()
@require_auth
def uofx_custom_send_notification(content: str, user_codes: list[str], title: str = "AI 小助理通知", user_type: int = 0) -> str:
    """發送內部系統通知。支援「個人」或「部門全體」模式(迴圈發送)。"""
    return send_system_notification(content, user_codes, title, user_type)

@mcp.tool()
@require_auth
def uofx_custom_get_pending_questionnaires(user_code: str) -> str:
    """查詢使用者的未填問卷"""
    return get_pending_questionnaires(user_code)

@mcp.tool()
@require_auth
def uofx_custom_get_iso_documents(keyword: str = "") -> str:
    """查詢 ISO 管制文件狀態"""
    return get_iso_documents(keyword)


def main():
    # 執行伺服器 (支援 stdio 等傳輸方式)
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
