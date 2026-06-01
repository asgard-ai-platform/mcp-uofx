from ..api_client import uofx_client

def get_department_manager(dept_code: str) -> str:
    """查詢特定部門的主管資訊"""
    try:
        response = uofx_client.get(f"/openapi/base/v1/department/manager/{dept_code}")
        manager = response.get("model")
        if not manager:
            return f"找不到代碼為 {dept_code} 的部門主管資訊。"
            
        name = manager.get("name") or manager.get("Name") or "未知姓名"
        code = manager.get("account") or manager.get("Code") or manager.get("UserCode") or "未知代碼"
        title = manager.get("businessCard") or manager.get("TitleName") or "主管"
        
        return f"部門 {dept_code} 的主管是 {name} ({title})，員工代號: {code}。"
    except Exception as e:
        return f"❌ 查詢部門主管時發生錯誤: {str(e)}"

def get_department_employees(dept_code: str) -> str:
    """查詢部門最新員工名單"""
    try:
        response = uofx_client.get(f"/openapi/base/v1/department/employee/{dept_code}/false")
        emps = response.get("model", [])
        if not emps:
            return f"部門 {dept_code} 找不到任何員工。"
            
        emp_list = []
        for i, emp in enumerate(emps[:10], 1):  # 取前 10 筆
            name = emp.get("name") or emp.get("UserName", "未知")
            code = emp.get("account") or emp.get("UserCode", "未知")
            emp_list.append(f"{i}. {name} ({code})")
            
        return f"部門 {dept_code} 共有 {len(emps)} 位員工，前10位如下：\n" + "\n".join(emp_list)
    except Exception as e:
        return f"❌ 查詢部門員工時發生錯誤: {str(e)}"

def get_my_profile(user_code: str, user_type: int = 0) -> str:
    """取得使用者的完整身份（姓名、部門、職稱等），所有其他 Tool 的前置必要步驟"""
    try:
        # 1. 取得基本資料
        profile_resp = uofx_client.get(f"/openapi/base/v1/employee/{user_type}/{user_code}")
        profile = profile_resp.get("model", {})
        if not profile:
            return f"找不到代碼為 {user_code} 的使用者基本資料。"
            
        # 2. 取得所屬部門與職務資訊
        dept_resp = uofx_client.get(f"/openapi/base/v1/employee/dept/{user_type}/{user_code}")
        depts = dept_resp.get("model", {}).get("depts", [])
        
        name = profile.get("name") or profile.get("UserName") or "未知姓名"
        account = profile.get("account") or profile.get("UserCode") or "未知帳號"
        
        dept_info = []
        is_manager = False
        managed_depts = []
        
        for dept in depts:
            dept_code = dept.get("code", "")
            dept_name = dept.get("name", "")
            title = dept.get("jobTitle", "")
            is_main = dept.get("isMainDept", False)
            main_tag = "(主要部門)" if is_main else ""
            dept_info.append(f"- {dept_name} ({dept_code}) {title} {main_tag}")
            
            # 判斷是否為主管，這裡需另外查詢該部門主管，或簡單視職稱/邏輯判斷
            # 這裡我們呼叫一下部門主管 API 來確認 (如果有權限的話)
            try:
                mgr_resp = uofx_client.get(f"/openapi/base/v1/department/manager/{dept_code}")
                mgr_model = mgr_resp.get("model")
                if mgr_model:
                    mgr_account = mgr_model.get("account") or mgr_model.get("UserCode")
                    if mgr_account == account:
                        is_manager = True
                        managed_depts.append(dept_code)
            except Exception:
                pass

        result = [
            f"👤 使用者資料：{name} ({account})",
            "所屬部門與職務："
        ]
        result.extend(dept_info)
        result.append(f"是否為主管：{'是' if is_manager else '否'}")
        if is_manager:
            result.append(f"管轄部門：{', '.join(managed_depts)}")
            
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢使用者基本資料時發生錯誤: {str(e)}"

def get_all_departments() -> str:
    """取得完整組織架構部門清單"""
    try:
        response = uofx_client.get("/openapi/base/v1/department")
        depts = response.get("model", [])
        if not depts:
            return "找不到任何部門資料。"
            
        result = ["🏢 組織架構清單："]
        # 先找根部門 (parentCode 為空或 None)
        def build_tree(parent_code, level=0):
            children = [d for d in depts if d.get("parentCode") == parent_code]
            # 若 parent_code 為 None，可能需要檢查空字串
            if parent_code is None:
                children.extend([d for d in depts if d.get("parentCode") == ""])
            
            for child in sorted(children, key=lambda x: x.get("seq", 0)):
                indent = "  " * level
                active = "" if child.get("active") else " (停用)"
                result.append(f"{indent}- {child.get('name')} ({child.get('code')}){active}")
                build_tree(child.get("code"), level + 1)
                
        build_tree(None)
        
        # 如果樹狀建構失敗(可能沒有 root)，降級為平坦列表
        if len(result) == 1:
            for dept in depts:
                active = "" if dept.get("active") else " (停用)"
                result.append(f"- {dept.get('name')} ({dept.get('code')}){active}")
                
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢部門清單時發生錯誤: {str(e)}"
