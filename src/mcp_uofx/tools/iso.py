from .dms import search_dms_document

def get_iso_documents(keyword: str = "") -> str:
    """查詢 ISO 管制文件庫（CONTROL）中的文件。keyword 為空時列出所有文件。"""
    # ISO 管制文件存放在 CONTROL 文件庫，使用 DMS 搜尋功能
    try:
        result = search_dms_document(keyword or "", folder_code="CONTROL")
        # 調整提示詞讓回傳更清晰
        if "找不到" in result or "無文件" in result:
            return "目前管制文件庫（CONTROL）中沒有文件，或關鍵字不符。"
        return result
    except Exception as e:
        return f"❌ 查詢 ISO 管制文件失敗: {str(e)}"
