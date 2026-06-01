from ..api_client import uofx_client


def _corp_code() -> str:
    return uofx_client.corp_code

def get_my_agent_settings(user_code: str, user_type: int = 0) -> str:
    """查詢使用者的代理人設定狀態（含 ID，可用於刪除）"""
    payload = {"userType": user_type, "userCode": user_code}
    try:
        response = uofx_client.post("/openapi/base/v1/agent/settings", payload=payload)
        model = response.get("model", {})

        agent_times = model.get("agentTimes", [])
        agent_users = model.get("agentUsers", [])

        result = [f"⚙️ {user_code} 的代理人設定：\n"]

        if agent_times:
            result.append(f"代理時間（共 {len(agent_times)} 筆）：")
            for i, t in enumerate(agent_times, 1):
                tid = t.get("id", "")
                start = t.get("startTime", "")
                end = t.get("endTime", "")
                result.append(f"  {i}. {start} ～ {end}")
                result.append(f"     [ID: {tid}]")
        else:
            result.append("代理時間：（無）")

        result.append("")

        if agent_users:
            # 整理：依 to[0].employee.userCode 去重顯示
            result.append(f"代理人設定（共 {len(agent_users)} 筆）：")
            for i, u in enumerate(agent_users, 1):
                uid = u.get("id", "")
                to_list = u.get("to", [])
                agent_user_code = "未知"
                if to_list:
                    emp = to_list[0].get("employee", {})
                    agent_user_code = emp.get("userCode", "未知")
                form_name = u.get("formName") or "（全部表單）"
                priority = u.get("priority", i - 1)
                result.append(f"  {i}. → {agent_user_code}  表單：{form_name}  優先序：{priority}")
                result.append(f"     [ID: {uid}]")
        else:
            result.append("代理人：（無）")

        result.append("\n💡 使用 delete_agent_time / delete_agent_user 可移除指定項目。")
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢代理設定失敗: {str(e)}"


def get_agent_forms(user_code: str, user_type: int = 0) -> str:
    """查詢使用者可代理的表單清單"""
    payload = {"userType": user_type, "userCode": user_code}
    try:
        response = uofx_client.post("/openapi/base/v1/agent/forms", payload=payload)
        forms = response.get("model", [])
        if not forms:
            return f"📋 {user_code} 目前沒有可代理的表單（代理全部表單時無需特別指定）。"

        result = [f"📋 {user_code} 可代理的表單清單："]
        for category in forms:
            cat_name = category.get("categoryName", "未分類")
            items = category.get("formItems", [])
            if items:
                result.append(f"\n📁 【{cat_name}】：")
                for item in items:
                    name = item.get('formName') or '（未命名）'
                    result.append(f"  - {name}  (formId: {item.get('formId')})")
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢可代理表單失敗: {str(e)}"


def set_agent_time(user_code: str, start_time: str, end_time: str, user_type: int = 0) -> str:
    """新增代理時間段（ISO8601，含時區 +08:00）。
    注意：不可與現有時間段重疊；若有衝突請先刪除舊設定。"""
    payload = {
        "user": {"userType": user_type, "userCode": user_code, "corpCode": _corp_code()},
        "startTime": start_time,
        "endTime": end_time
    }
    try:
        uofx_client.post("/openapi/base/v1/agent/time", payload=payload)
        uofx_client.post("/openapi/base/v1/permission/update", payload={})
        return f"✅ 成功為 {user_code} 新增代理時間：{start_time} ～ {end_time}"
    except Exception as e:
        return f"❌ 設定代理時間失敗: {str(e)}\n💡 提示：若出現 400，可能是時間段與現有設定重疊，請先查詢並刪除舊設定。"


def delete_agent_time(user_code: str, time_id: str, user_type: int = 0) -> str:
    """刪除指定的代理時間段（time_id 從 get_my_agent_settings 取得）"""
    payload = {
        "user": {"userType": user_type, "userCode": user_code, "corpCode": _corp_code()},
        "id": time_id
    }
    try:
        uofx_client.delete("/openapi/base/v1/agent/time", payload=payload)
        uofx_client.post("/openapi/base/v1/permission/update", payload={})
        return f"✅ 成功刪除 {user_code} 的代理時間段（ID: {time_id}）"
    except Exception as e:
        return f"❌ 刪除代理時間失敗: {str(e)}"


def set_agent_user(user_code: str, agent_user_code: str, user_type: int = 0, agent_user_type: int = 0, from_dept_code: str = "") -> str:
    """新增代理人（不填 from_dept_code 表示代理全部部門的表單）"""
    payload = {
        "user": {"userType": user_type, "userCode": user_code, "corpCode": _corp_code()},
        "from": [{"deptCode": from_dept_code}] if from_dept_code else [],
        "to": {
            "employee": {"userType": agent_user_type, "userCode": agent_user_code, "corpCode": _corp_code()}
        },
        "priority": 0
    }
    try:
        uofx_client.post("/openapi/base/v1/agent/user", payload=payload)
        uofx_client.post("/openapi/base/v1/permission/update", payload={})
        return f"✅ 成功將 {user_code} 的代理人設定為 {agent_user_code}"
    except Exception as e:
        return f"❌ 設定代理人失敗: {str(e)}"


def delete_agent_user(user_code: str, agent_id: str, user_type: int = 0) -> str:
    """刪除指定的代理人設定（agent_id 從 get_my_agent_settings 取得）"""
    payload = {
        "user": {"userType": user_type, "userCode": user_code, "corpCode": _corp_code()},
        "id": agent_id
    }
    try:
        uofx_client.delete("/openapi/base/v1/agent/user", payload=payload)
        uofx_client.post("/openapi/base/v1/permission/update", payload={})
        return f"✅ 成功刪除 {user_code} 的代理人設定（ID: {agent_id}）"
    except Exception as e:
        return f"❌ 刪除代理人失敗: {str(e)}"
