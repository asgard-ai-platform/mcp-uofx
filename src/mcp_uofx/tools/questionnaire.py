from ..api_client import uofx_client

def get_pending_questionnaires(user_code: str) -> str:
    """查詢未填寫的問卷"""
    payload = {
        "UserCode": user_code
    }
    try:
        response = uofx_client.post("/openapi/eip/v1/que/list", payload=payload)
        ques = response.get("model", [])
        if not ques:
            return f"🎉 {user_code} 目前沒有需要填寫的問卷。"
            
        que_list = []
        for i, que in enumerate(ques, 1):
            title = que.get("Title", "未命名問卷")
            end_time = que.get("EndTime", "無期限")
            que_list.append(f"{i}. {title} (截止日: {end_time})")
            
        return f"📋 您有 {len(ques)} 份待填問卷：\n" + "\n".join(que_list)
    except Exception as e:
        return f"❌ 查詢問卷失敗: {str(e)}"
