from ..api_client import uofx_client


def search_dms_document(keyword: str, folder_code: str = None, folder_path: str = None, category: int = 0) -> str:
    """搜尋 DMS 文件庫中的文件。
    keyword: 檔名關鍵字
    folder_code: 文件庫根目錄代碼 (預設 GENERAL)
    folder_path: 指定搜尋的資料夾路徑 (如 /公司規章/人事管理)
    category: 0=全部, 1=草稿, 2=發行, 3=作廢
    """
    if not folder_code:
        try:
            root_response = uofx_client.get("/openapi/dms/v1/folder/root")
            root_folders = root_response.get("model", [])
            if root_folders:
                folder_code = root_folders[0].get("code", "")
        except Exception:
            pass

    if not folder_code:
        return "❌ 搜尋失敗：未找到可用的文件庫目錄。"

    # 如果指定了路徑就搜那個路徑；否則遍歷多層資料夾
    if folder_path:
        search_paths = [folder_path]
    else:
        # 嘗試在根目錄取得子資料夾清單，然後逐層搜尋（只搜葉子資料夾）
        search_paths = []
        leaf_paths = []
        try:
            resp = uofx_client.get(f"/openapi/dms/v1/folder/list/{folder_code}")
            top_folders = resp.get("model", [])
            for f in top_folders:
                name = f.get("path") or f.get("name", "")
                if not name:
                    continue
                # 查第二層子資料夾
                has_children = False
                try:
                    payload_sub = {
                        "keyword": "",
                        "rootFolderCode": folder_code,
                        "folderPath": f"/{name}",
                        "category": 0,
                        "pageOptions": {"page": 0, "size": 50}
                    }
                    resp2 = uofx_client.post("/openapi/dms/v1/doc/list", payload=payload_sub)
                    model2 = resp2.get("model", {})
                    items2 = model2.get("items", []) if isinstance(model2, dict) else []
                    for item in items2:
                        if item.get("folder") and not item.get("document"):
                            sub_name = item["folder"]
                            leaf_paths.append(f"/{name}/{sub_name}")
                            has_children = True
                        elif item.get("document"):
                            # 這個資料夾本身也有文件
                            if f"/{name}" not in leaf_paths:
                                leaf_paths.append(f"/{name}")
                except Exception:
                    pass
                if not has_children:
                    leaf_paths.append(f"/{name}")
        except Exception:
            leaf_paths = ["/"]
        search_paths = leaf_paths if leaf_paths else ["/"]

    all_docs = []
    seen_ids = set()
    for sp in search_paths:
        payload = {
            "keyword": keyword,
            "rootFolderCode": folder_code,
            "folderPath": sp,
            "category": category,
            "pageOptions": {"page": 0, "size": 20}
        }
        try:
            response = uofx_client.post("/openapi/dms/v1/doc/list", payload=payload)
            model = response.get("model", {})
            items = model.get("items", []) if isinstance(model, dict) else (model if isinstance(model, list) else [])
            for item in items:
                doc = item.get("document")
                if doc:
                    doc_id = doc.get("id", "")
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        item["_searchPath"] = sp
                        all_docs.append(item)
        except Exception:
            continue

    # 過濾：如果 keyword 不為空，嘗試用檔名匹配來排序（API 可能回傳所有文件）
    if keyword:
        matched = [d for d in all_docs if keyword in d.get("document", {}).get("fileName", "")]
        unmatched = [d for d in all_docs if keyword not in d.get("document", {}).get("fileName", "")]
        all_docs = matched + unmatched

    if not all_docs:
        return f"找不到包含『{keyword}』的文件。"

    doc_list = []
    for i, item in enumerate(all_docs[:10], 1):
        doc = item.get("document", {})
        file_name = doc.get("fileName", "未命名文件")
        file_size = doc.get("length", 0)
        path = item.get("_searchPath", "/")
        size_str = f"{file_size/1024:.1f}KB" if file_size > 0 else ""
        doc_list.append(f"{i}. 📄 {file_name} ({size_str}) — 路徑: {path}")

    return f"📁 找到 {len(all_docs)} 筆包含『{keyword}』的文件：\n" + "\n".join(doc_list)


def list_dms_folders(root_code: str = None) -> str:
    """查詢 DMS 文件目錄結構。不指定 root_code 則回傳所有根目錄及其子目錄；指定則回傳該目錄的子資料夾。"""
    try:
        if root_code:
            # 查詢指定根目錄的子資料夾
            response = uofx_client.get(f"/openapi/dms/v1/folder/list/{root_code}")
            folders = response.get("model", [])
            prefix = f"📁 目錄 {root_code} 的子資料夾："

            if not folders:
                return f"{prefix}\n  (無子資料夾)"

            result = [prefix]
            for folder in folders:
                name = folder.get("name", "未命名目錄")
                path = folder.get("path", name)
                result.append(f"  - {name} (路徑: /{path})")
            return "\n".join(result)
        else:
            # 回傳所有根目錄（一般 + 管制）
            result = ["📁 DMS 文件庫目錄清單："]

            # 一般文件庫
            gen_resp = uofx_client.get("/openapi/dms/v1/folder/root")
            gen_roots = gen_resp.get("model", [])
            for root in gen_roots:
                code = root.get("code", "?")
                name = root.get("name", "未命名")
                result.append(f"\n📂 {name} (代碼: {code}, 類型: 一般文件庫)")
                # 列出子資料夾
                try:
                    sub_resp = uofx_client.get(f"/openapi/dms/v1/folder/list/{code}")
                    for sf in sub_resp.get("model", []):
                        result.append(f"  └─ {sf.get('name', '?')} (路徑: /{sf.get('path', sf.get('name', ''))})")
                except Exception:
                    pass

            # 管制文件庫
            iso_resp = uofx_client.get("/openapi/dms/v1/iso/folder/root")
            iso_roots = iso_resp.get("model", [])
            for root in iso_roots:
                code = root.get("code", "?")
                name = root.get("name", "未命名")
                result.append(f"\n📂 {name} (代碼: {code}, 類型: 管制文件庫)")
                try:
                    sub_resp = uofx_client.get(f"/openapi/dms/v1/iso/folder/list/{code}")
                    for sf in sub_resp.get("model", []):
                        result.append(f"  └─ {sf.get('name', '?')} (路徑: /{sf.get('path', sf.get('name', ''))})")
                except Exception:
                    pass

            return "\n".join(result)
    except Exception as e:
        return f"❌ 查詢目錄清單時發生錯誤: {str(e)}"
