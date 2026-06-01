from ..api_client import uofx_client

def get_pending_bpm_tasks(user_code: str, user_type: int = 0) -> str:
    """查詢個人的待辦簽核表單盤點"""
    payload = {
        "user": {
            "userType": user_type,
            "userCode": user_code
        },
        "taskStatus": 0,
        "pageOptions": {
            "page": 0,
            "size": 50,
            "order": 0,
            "by": 0
        }
    }
    
    try:
        response = uofx_client.post("/openapi/bpm/v1/form/search/task/todo", payload=payload)
        model = response.get("model", {})
        tasks = model.get("items", [])
        
        if not tasks:
            return f"🎉 {user_code} 目前沒有任何待處理的表單簽核。"
            
        task_list = []
        for i, task in enumerate(tasks, 1):
            form_name = task.get("formName", "未命名表單")
            subject = task.get("subject", "無主旨")
            form_sn = task.get("formSn", "無單號")
            url = task.get("url", "")
            url_hint = f"\n   🔗 {url}" if url else ""
            task_list.append(f"{i}. [{form_name}] {subject} (單號: {form_sn}){url_hint}")
            
        total_count = model.get("pageInfo", {}).get("itemsCount", len(tasks))
        return f"📌 {user_code} 共有 {total_count} 件待辦簽核：\n" + "\n".join(task_list)
        
    except Exception as e:
        return f"❌ 查詢待辦表單時發生錯誤: {str(e)}"

def apply_bpm_form(form_id: str, applicant_code: str, applicant_dept_code: str, fields: list, applicant_type: int = 0) -> str:
    """主動發起外部表單"""
    payload = {
        "applyAccount": {
            "userType": applicant_type,
            "userCode": applicant_code
        },
        "deptCode": applicant_dept_code,
        "fields": fields,
        "urgent": False
    }
    try:
        # 這裡的 form_id 是起單的表單代號 (FormCode) 或 ID
        response = uofx_client.post(f"/openapi/bpm/v1/form/apply/{form_id}", payload=payload)
        trace_id = response.get("model")
        return f"✅ 成功為 {applicant_code} 發起表單 {form_id}。追蹤 ID (TraceId): {trace_id} (請另外查詢起單結果)"
    except Exception as e:
        return f"❌ 發起表單失敗: {str(e)}"

def get_available_forms(user_code: str, user_type: int = 0) -> str:
    """查詢使用者可發起的表單"""
    try:
        response = uofx_client.get(f"/openapi/bpm/v1/form/apply/{user_type}/{user_code}")
        model = response.get("model", {}) if isinstance(response, dict) else {}
        
        # Response: { "categoryList": [...], "formList": [{formCode, formName, category, ...}] }
        form_list = model.get("formList", [])
        
        if not form_list:
            return f"找不到 {user_code} 可發起的表單。"
            
        # 按 category 分組
        by_cat = {}
        for form in form_list:
            cat = form.get("category", "未分類")
            by_cat.setdefault(cat, []).append(form)
            
        result = [f"📋 {user_code} 可發起的表單清單："]
        for cat, forms in by_cat.items():
            result.append(f"\n📁 【{cat}】:")
            for form in forms:
                code = form.get("formCode", "")
                name = form.get("name", "")
                result.append(f"  - {name} (代碼: {code})")
                    
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢可發起表單時發生錯誤: {str(e)}"

def get_form_fields(form_code_or_id: str) -> str:
    """查詢起單時所需的欄位格式（傳入 formCode 或 formId）"""
    try:
        response = uofx_client.get(f"/openapi/bpm/v1/form/fields/{form_code_or_id}")
        model = response.get("model", {}) if isinstance(response, dict) else {}
        fields = model.get("fields", []) if isinstance(model, dict) else []
        
        if not fields:
            return f"表單 {form_code_or_id} 沒有欄位，或表單代碼不正確。"
            
        result = [f"📝 表單 {form_code_or_id} 的欄位清單："]
        for field in (fields if isinstance(fields, list) else []):
            is_required = " (必填)" if field.get("required") or field.get("isRequired") else ""
            not_support = " ⚠️系統元件" if field.get("notSupport") else ""
            field_id = field.get("code") or field.get("id", "")
            field_name = field.get("name", "")
            field_type = field.get("typeId") or field.get("fieldType", "")
            result.append(f"- [{field_id}] {field_name} (type: {field_type}){is_required}{not_support}")
            
        result.append("\n💡 提示: 發起表單時，請依照上述 fieldId 提供對應的值。")
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢表單欄位時發生錯誤: {str(e)}"

def get_task_detail(form_sn: str) -> str:
    """查詢單據詳細內容（傳入表單單號 formSn 或任務 ID）"""
    try:
        response = uofx_client.get(f"/openapi/bpm/v1/form/task/content/{form_sn}")
        task = response.get("model", {}) if isinstance(response, dict) else {}
        
        if not task:
            return f"找不到單號 {form_sn} 的詳細資訊。"
            
        form_name = task.get("formName", "未命名表單")
        subject = task.get("subject", "無主旨")
        applicant = task.get("applicant") or {}
        applicant_name = applicant.get("name", "未知申請人") if isinstance(applicant, dict) else str(applicant)
        status = task.get("formStatus", 0)
        
        status_map = {0: "處理中", 1: "結案(同意)", 2: "結案(否決)", 3: "結案(作廢)", 4: "異常"}
        status_str = status_map.get(status, f"未知({status})")
        
        result = [
            f"📄 單據詳情：{form_name}",
            f"- 單號: {task.get('formSn', form_sn)}",
            f"- 主旨: {subject}",
            f"- 申請人: {applicant_name}",
            f"- 狀態: {status_str}",
            f"- 申請時間: {task.get('applicantDate', task.get('applyTime', '未知時間'))}"
        ]
        
        fields = task.get("fields", [])
        if fields:
            result.append("\n📋 表單欄位：")
            for f in fields[:10]:
                result.append(f"  - {f.get('fieldName', '')}: {f.get('fieldValue', '')}")
        
        return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢單據詳情時發生錯誤: {str(e)}"
