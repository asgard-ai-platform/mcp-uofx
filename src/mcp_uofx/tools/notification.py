from ..api_client import uofx_client

def send_system_notification(content: str, user_codes: list[str], title: str = "AI 小助理通知", user_type: int = 0) -> str:
    """發送內部系統通知 (由於 API 每次只能發送給單一人員，此工具會自動進行迴圈)"""
    success_count = 0
    errors = []
    
    for code in user_codes:
        payload = {
            "to": {
                "userType": user_type,
                "userCode": code
            },
            "title": title,
            "message": content
        }
        try:
            uofx_client.post("/openapi/notify/v1/personal", payload=payload)
            success_count += 1
        except Exception as e:
            errors.append(f"{code}: {str(e)}")
            
    if not errors:
        return f"✅ 成功發送通知給 {success_count} 位使用者。"
    else:
        error_msg = "\n".join(errors)
        return f"⚠️ 發送完成。成功: {success_count} 位，失敗: {len(errors)} 位。\n錯誤細節:\n{error_msg}"
