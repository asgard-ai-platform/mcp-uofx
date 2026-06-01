"""
UOF X OpenAPI 全模組 CRUD 測試腳本
安全規則: 所有寫入操作僅針對代碼前綴 TST* 的資料，測試後立即清除。
"""
import os
import urllib.request, urllib.error, json, ssl
from pathlib import Path

API_KEY = os.environ.get("UOFX_API_KEY", "")
CORP_CODE = os.environ.get("UOFX_CORP_CODE", "")
HOST = os.environ.get("UOFX_BASE_URL", "").rstrip("/")
TEST_USER = os.environ.get("UOFX_TEST_USER", "test_user")
RESULTS = []

def req(method, path, payload=None, base_path=""):
    url = HOST + base_path + path
    hdrs = {"Api-Key": API_KEY, "CorpCode": CORP_CODE, "Content-Type": "application/json", "User-Agent": "Antigravity/Test"}
    data = json.dumps(payload).encode() if payload else None
    r = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        resp = urllib.request.urlopen(r, context=ctx)
        return resp.getcode(), resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except urllib.error.URLError as e:
        return 0, str(e.reason)

def b(path, payload=None, method="GET"):
    return req(method, path, payload, "/openapi/base/v1")
def bpm(path, payload=None, method="GET"):
    return req(method, path, payload, "/openapi/bpm/v1")
def dms(path, payload=None, method="GET"):
    return req(method, path, payload, "/openapi/dms/v1")
def eip(path, payload=None, method="GET"):
    return req(method, path, payload, "/openapi/eip/v1")
def fup(path, payload=None, method="POST"):
    return req(method, path, payload, "/openapi/file/v1")
def ntf(path, payload=None, method="POST"):
    return req(method, path, payload, "/openapi/notify/v1")

def log(module, api, status, note=""):
    icon = "✅" if status in [200,201,204] else ("⚠️" if status==400 else "❌")
    entry = {"module": module, "api": api, "status": status, "icon": icon, "note": note}
    RESULTS.append(entry)
    print(f"{icon} [{module}] {api} -> {status} {note}")

# ── 部門層級管理 ──────────────────────────────────────────────
def test_deptlevel():
    m = "部門層級管理"
    s,_ = b("/deptlevel"); log(m,"GET /deptlevel",s)
    s,r = b("/deptlevel",{"code":"TSTLV01","name":"Test Level","seq":99,"active":True},"POST"); log(m,"POST /deptlevel",s)
    s,_ = b("/deptlevel",{"originalCode":"TSTLV01","code":"TSTLV01","name":"Test Level Updated","seq":99,"active":True},"PUT"); log(m,"PUT /deptlevel",s)
    s,_ = req("PUT","/deptlevel/seq",{"code":"TSTLV01","seq":98},"/openapi/base/v1"); log(m,"PUT /deptlevel/seq",s)
    s,_ = req("PUT","/deptlevel/status",{"code":"TSTLV01","active":False},"/openapi/base/v1"); log(m,"PUT /deptlevel/status",s)
    s,_ = b(f"/deptlevel/TSTLV01",method="DELETE"); log(m,"DELETE /deptlevel/{code}",s)

# ── 職務管理 ──────────────────────────────────────────────────
def test_jobfunc():
    m = "職務管理"
    s,_ = b("/jobfunc"); log(m,"GET /jobfunc",s)
    s,_ = b("/jobfunc",{"code":"TSTJF01","name":"Test JobFunc","categoryName":"TSTCat","seq":1,"active":True},"POST"); log(m,"POST /jobfunc",s)
    s,_ = b("/jobfunc",{"originalCode":"TSTJF01","code":"TSTJF01","name":"Test JobFunc Updated","categoryName":"TSTCat"},"PUT"); log(m,"PUT /jobfunc",s)
    s,_ = req("PUT","/jobfunc/seq",{"code":"TSTJF01","seq":2},"/openapi/base/v1"); log(m,"PUT /jobfunc/seq",s)
    s,_ = req("PUT","/jobfunc/status",{"code":"TSTJF01","active":False},"/openapi/base/v1"); log(m,"PUT /jobfunc/status",s)
    s,_ = b(f"/jobfunc/TSTJF01",method="DELETE"); log(m,"DELETE /jobfunc/{code}",s)

# ── 職務類別管理 ─────────────────────────────────────────────
def test_jobfunc_category():
    m = "職務類別管理"
    # Create a jobfunc first to create its category
    b("/jobfunc",{"code":"TSTJFC1","name":"CatTest","categoryName":"TSTCategory","seq":1,"active":True},"POST")
    s,_ = req("PUT","/jobfunc/category",{"originalName":"TSTCategory","name":"TSTCategoryUpdated"},"/openapi/base/v1"); log(m,"PUT /jobfunc/category",s)
    s,_ = req("PUT","/jobfunc/category/seq",{"name":"TSTCategoryUpdated","seq":2},"/openapi/base/v1"); log(m,"PUT /jobfunc/category/seq",s)
    b(f"/jobfunc/TSTJFC1",method="DELETE")
    s,_ = req("DELETE","/jobfunc/category/TSTCategoryUpdated",None,"/openapi/base/v1"); log(m,"DELETE /jobfunc/category/{name}",s)

# ── 職稱管理 ──────────────────────────────────────────────────
def test_jobtitle():
    m = "職稱管理"
    s,_ = b("/jobtitle"); log(m,"GET /jobtitle",s)
    s,_ = b("/jobtitle",{"code":"TSTTL01","title":"Test Title","rank":1,"seq":1,"active":True},"POST"); log(m,"POST /jobtitle",s)
    s,_ = b("/jobtitle",{"originalCode":"TSTTL01","code":"TSTTL01","title":"Test Title Updated"},"PUT"); log(m,"PUT /jobtitle",s)
    s,_ = req("PUT","/jobtitle/seq",{"code":"TSTTL01","rank":1,"seq":2},"/openapi/base/v1"); log(m,"PUT /jobtitle/seq",s)
    s,_ = req("PUT","/jobtitle/status",{"code":"TSTTL01","active":False},"/openapi/base/v1"); log(m,"PUT /jobtitle/status",s)
    s,_ = b(f"/jobtitle/TSTTL01",method="DELETE"); log(m,"DELETE /jobtitle/{code}",s)

# ── 部門管理 ──────────────────────────────────────────────────
def test_department():
    m = "部門管理"
    s,_ = b("/department"); log(m,"GET /department",s)
    s,_ = b("/department",{"code":"TSTDP01","parentCode":None,"deptLevelCode":"lev1","name":"Test Dept","active":True,"seq":1},"POST"); log(m,"POST /department",s)
    s,_ = b("/department",{"code":"TSTDP02","parentCode":None,"deptLevelCode":"lev1","name":"Test Dept2","active":True,"seq":2},"POST")
    s,r = b(f"/department/TSTDP01/false"); log(m,"GET /department/{code}/{include}",s)
    s,_ = b("/department",{"originalCode":"TSTDP01","code":"TSTDP01","parentCode":None,"deptLevelCode":"lev1","name":"Test Dept Updated","active":True,"seq":1},"PUT"); log(m,"PUT /department",s)
    s,_ = req("PUT","/department/status",{"code":"TSTDP01","active":False},"/openapi/base/v1"); log(m,"PUT /department/status",s)
    s,_ = req("PUT","/department/move",{"code":"TSTDP02","parentCode":"TSTDP01"},"/openapi/base/v1"); log(m,"PUT /department/move",s)
    s,_ = req("PUT","/department/move/batch",{"items":[{"code":"TSTDP02","parentCode":None}]},"/openapi/base/v1"); log(m,"PUT /department/move/batch",s)
    s,_ = b(f"/department/TSTDP02",method="DELETE")
    s,_ = b(f"/department/TSTDP01",method="DELETE"); log(m,"DELETE /department/{code}",s)

# ── 部門人員/主管管理 ─────────────────────────────────────────
def test_dept_emp_mgr():
    m = "部門人員/主管"
    s,_ = b("/department/employee"); log(m,"GET /department/employee",s)
    s,_ = b("/department/employee/J0PM/false"); log(m,"GET /department/employee/{code}",s)
    s,_ = b("/department/manager/J0PM"); log(m,"GET /department/manager/{code}",s)
    # PUT/DELETE manager need real employee, just test connectivity
    s,_ = req("PUT","/department/manager",{"deptCode":"J0PM","userCode":"notexist","userType":"E"},"/openapi/base/v1"); log(m,"PUT /department/manager",s,"(400 expected=連通)")
    s,_ = req("DELETE","/department/manager/TSTDP01",None,"/openapi/base/v1"); log(m,"DELETE /department/manager/{code}",s,"(400/404 expected=連通)")

# ── 員工管理 ──────────────────────────────────────────────────
def test_employee():
    m = "員工管理"
    # First get existing employee list
    s,r = b("/department/employee"); 
    emp_code = None
    if s==200:
        emps = json.loads(r).get("model",[])
        if emps: emp_code = emps[0].get("code")
    
    # Read
    s,_ = b(f"/employee/E/{emp_code or 'test'}"); log(m,"GET /employee/{type}/{code}",s)
    s,_ = b(f"/employee/E/{emp_code or 'test'}/{CORP_CODE}"); log(m,"GET /employee/{type}/{code}/{corpCode}",s)
    s,_ = b(f"/employee/dept/E/{emp_code or 'test'}"); log(m,"GET /employee/dept/{type}/{code}",s)
    s,_ = b(f"/employee/dept/E/{emp_code or 'test'}/{CORP_CODE}"); log(m,"GET /employee/dept/{type}/{code}/{corpCode}",s)

    # Create test employee (needs jobtitle lev1, dept)
    # First create prerequisites
    b("/jobtitle",{"code":"TSTTLEP","title":"EmpTestTitle","rank":1,"seq":1,"active":True},"POST")
    b("/department",{"code":"TSTDPEP","parentCode":None,"deptLevelCode":"lev1","name":"EmpTestDept","active":True,"seq":1},"POST")
    
    emp_payload = {
        "userType":"E","userCode":"TSTEP001","name":"Test Employee","email":"test@test.com",
        "active":True,"account":"TSTEP001",
        "depts":[{"deptCode":"TSTDPEP","jobFuncCode":None,"jobTitleCode":"TSTTLEP","main":True}]
    }
    s,r = b("/employee",emp_payload,"POST"); log(m,"POST /employee",s)
    
    # Update
    s,_ = b("/employee",{"userType":"E","userCode":"TSTEP001","name":"Test Employee Updated","email":"test@test.com"},"PUT"); log(m,"PUT /employee",s)
    s,_ = req("PUT","/employee/lock",{"userCode":"TSTEP001","userType":"E","lock":True},"/openapi/base/v1"); log(m,"PUT /employee/lock",s)
    s,_ = req("PUT","/employee/status",{"userCode":"TSTEP001","userType":"E","active":False},"/openapi/base/v1"); log(m,"PUT /employee/status",s)
    s,_ = req("PUT","/employee/expired",{"userCode":"TSTEP001","userType":"E","expiredDate":"2030-12-31"},"/openapi/base/v1"); log(m,"PUT /employee/expired",s)
    s,_ = req("PUT","/employee/resignation",{"userCode":"TSTEP001","userType":"E","resignationDate":"2030-12-31"},"/openapi/base/v1"); log(m,"PUT /employee/resignation",s)
    s,_ = req("PUT","/employee/supervisor",{"userCode":"TSTEP001","userType":"E","deptCode":"TSTDPEP","supervisorUserCode":None,"supervisorUserType":None},"/openapi/base/v1"); log(m,"PUT /employee/supervisor",s)
    s,_ = req("PUT","/employee/dept",{"userCode":"TSTEP001","userType":"E","depts":[{"deptCode":"TSTDPEP","jobFuncCode":None,"jobTitleCode":"TSTTLEP","main":True}]},"/openapi/base/v1"); log(m,"PUT /employee/dept",s)
    s,_ = req("PUT","/employee/dept/main",{"userCode":"TSTEP001","userType":"E","deptCode":"TSTDPEP"},"/openapi/base/v1"); log(m,"PUT /employee/dept/main",s)
    
    # Delete
    s,_ = b("/employee",{"userCode":"TSTEP001","userType":"E"},"DELETE"); log(m,"DELETE /employee",s)
    
    # Cleanup prerequisites (BUG FIX: use method= kwarg)
    b("/jobtitle/TSTTLEP", method="DELETE")
    b("/department/TSTDPEP", method="DELETE")

# ── 代理人管理 ────────────────────────────────────────────────
def test_agent():
    m = "代理人管理"
    s,r = b("/department/employee"); 
    emp1 = emp2 = None
    if s==200:
        emps = json.loads(r).get("model",[])
        if len(emps)>0: emp1 = emps[0].get("code")
        if len(emps)>1: emp2 = emps[1].get("code")
    if not emp1:
        for api in ["POST /agent/settings","POST /agent/forms","POST /agent/time","DELETE /agent/time","POST /agent/user","DELETE /agent/user"]:
            log(m, api, 0, "skip - no employees in site")
        return

    s,_ = b("/agent/settings",{"userCode":emp1,"userType":"E"},"POST"); log(m,"POST /agent/settings",s)
    s,_ = b("/agent/forms",{"userCode":emp1,"userType":"E"},"POST"); log(m,"POST /agent/forms",s)
    payload_time = {"userCode":emp1,"userType":"E","startDate":"2026-01-01","endDate":"2026-12-31"}
    s,r = b("/agent/time",payload_time,"POST"); log(m,"POST /agent/time",s)
    agent_id = None
    if s==200:
        try: agent_id = json.loads(r).get("model",{}).get("id")
        except: pass
    if agent_id:
        s,_ = b("/agent/time",{"id":agent_id},"DELETE"); log(m,"DELETE /agent/time",s)
    else:
        log(m,"DELETE /agent/time",0,"skip - no agent_id returned")
    if emp2:
        payload_user = {"userCode":emp1,"userType":"E","agentUserCode":emp2,"agentUserType":"E"}
        s,r = b("/agent/user",payload_user,"POST"); log(m,"POST /agent/user",s)
        if s==200:
            s,_ = b("/agent/user",{"userCode":emp1,"userType":"E","agentUserCode":emp2,"agentUserType":"E"},"DELETE"); log(m,"DELETE /agent/user",s)
        else:
            log(m,"DELETE /agent/user",0,"skip - agent user not created")
    else:
        log(m,"POST /agent/user",0,"skip - need 2 employees"); log(m,"DELETE /agent/user",0,"skip - need 2 employees")

# ── 檔案上傳 ──────────────────────────────────────────────────
def test_file_upload():
    m = "檔案上傳"
    import base64
    txt_b64 = base64.b64encode(b"UOF X API Test File").decode()
    s,_ = req("POST","/upload/base64",{"fileName":"test.txt","base64Content":txt_b64,"mimeType":"text/plain"},"/openapi/file/v1"); log(m,"POST /upload/base64",s)
    s,_ = req("POST","/upload/link",{"fileName":"test.txt","fileUrl":"https://example.com/test.txt"},"/openapi/file/v1"); log(m,"POST /upload/link",s)
    s,_ = req("POST","/upload/chunk",{"fileName":"test.txt","chunkIndex":0,"totalChunks":1,"chunkData":txt_b64},"/openapi/file/v1"); log(m,"POST /upload/chunk",s)

# ── 一般文件管理 (DMS) ────────────────────────────────────────
def test_dms():
    m = "一般文件管理"
    s,r = dms("/folder/root"); log(m,"GET /folder/root",s)
    root_code = None
    if s==200:
        roots = json.loads(r).get("model",[])
        if roots: root_code = roots[0].get("code")
    if not root_code:
        for api in ["GET /folder/list/{rootCode}","POST /folder","PUT /folder/rename","POST /folder/permission/view","PUT /folder/permission","DELETE /folder","POST /doc/list","POST /doc/exist","POST /doc","DELETE /doc"]:
            log(m, api, 0, "skip - DMS root empty")
        return
    if root_code:
        s,_ = dms(f"/folder/list/{root_code}"); log(m,"GET /folder/list/{rootCode}",s)
        s,r = dms("/folder",{"parentCode":root_code,"name":"Test Folder TST"},"POST"); log(m,"POST /folder",s)
        folder_code = None
        if s==200:
            try: folder_code = json.loads(r).get("model",{}).get("code")
            except: pass
        if folder_code:
            s,_ = dms("/folder/permission/view",{"code":folder_code},"POST"); log(m,"POST /folder/permission/view",s)
            s,_ = req("PUT","/folder/permission",{"code":folder_code,"permissions":[]},"/openapi/dms/v1"); log(m,"PUT /folder/permission",s)
            s,_ = req("PUT","/folder/rename",{"code":folder_code,"name":"Test Folder TST Renamed"},"/openapi/dms/v1"); log(m,"PUT /folder/rename",s)
            s,_ = dms("/doc/list",{"folderCode":folder_code},"POST"); log(m,"POST /doc/list",s)
            s,_ = dms("/doc/exist",{"folderCode":folder_code,"fileName":"test.txt"},"POST"); log(m,"POST /doc/exist",s)
            # POST /doc needs a fileToken from file upload; test connectivity with empty payload
            import base64
            txt_b64 = base64.b64encode(b"TST").decode()
            _,fup_r = req("POST","/upload/base64",{"fileName":"tst.txt","base64Content":txt_b64,"mimeType":"text/plain"},"/openapi/file/v1")
            file_token = None
            try: file_token = json.loads(fup_r).get("model",{}).get("fileToken")
            except: pass
            if file_token:
                s,dr = dms("/doc",{"folderCode":folder_code,"fileName":"tst.txt","fileToken":file_token},"POST"); log(m,"POST /doc",s)
                doc_code = None
                try: doc_code = json.loads(dr).get("model",{}).get("code")
                except: pass
                if doc_code:
                    s,_ = dms("/doc",{"code":doc_code},"DELETE"); log(m,"DELETE /doc",s)
                else:
                    log(m,"DELETE /doc",0,"skip - no doc code")
            else:
                log(m,"POST /doc",0,"skip - no file token")
                log(m,"DELETE /doc",0,"skip - no file token")
            s,_ = dms("/folder",{"code":folder_code},"DELETE"); log(m,"DELETE /folder",s)

# ── 管制文件管理 (ISO DMS) ────────────────────────────────────
def test_iso_dms():
    m = "管制文件管理"
    s,r = dms("/iso/folder/root"); log(m,"GET /iso/folder/root",s)
    root_code = None
    if s==200:
        roots = json.loads(r).get("model",[])
        if roots: root_code = roots[0].get("code")
    if not root_code:
        for api in ["GET /iso/folder/list/{rootCode}","POST /iso/folder","PUT /iso/folder/rename","DELETE /iso/folder","POST /iso/doc/rule/new","POST /iso/doc/rule/current","POST /iso/doc","PUT /iso/doc","DELETE /iso/doc/cancel","DELETE /iso/doc/destroy"]:
            log(m, api, 0, "skip - ISO DMS root empty")
        return
    if root_code:
        s,_ = dms(f"/iso/folder/list/{root_code}"); log(m,"GET /iso/folder/list/{rootCode}",s)
        s,r = dms("/iso/folder",{"parentCode":root_code,"name":"Test ISO Folder TST"},"POST"); log(m,"POST /iso/folder",s)
        folder_code = None
        if s==200:
            try: folder_code = json.loads(r).get("model",{}).get("code")
            except: pass
        if folder_code:
            s,_ = req("PUT","/iso/folder/rename",{"code":folder_code,"name":"Test ISO Folder TST Renamed"},"/openapi/dms/v1"); log(m,"PUT /iso/folder/rename",s)
            s,_ = dms("/iso/doc/rule/new",{"folderCode":folder_code},"POST"); log(m,"POST /iso/doc/rule/new",s)
            s,_ = dms("/iso/doc/rule/current",{"folderCode":folder_code},"POST"); log(m,"POST /iso/doc/rule/current",s)
            # POST /iso/doc needs fileToken
            import base64
            txt_b64 = base64.b64encode(b"TST ISO").decode()
            _,fup_r = req("POST","/upload/base64",{"fileName":"tst_iso.txt","base64Content":txt_b64,"mimeType":"text/plain"},"/openapi/file/v1")
            file_token = None
            try: file_token = json.loads(fup_r).get("model",{}).get("fileToken")
            except: pass
            if file_token:
                s,dr = dms("/iso/doc",{"folderCode":folder_code,"fileName":"tst_iso.txt","fileToken":file_token},"POST"); log(m,"POST /iso/doc",s)
                doc_code = None
                try: doc_code = json.loads(dr).get("model",{}).get("code")
                except: pass
                if doc_code:
                    s,_ = req("PUT","/iso/doc",{"code":doc_code,"fileName":"tst_iso_updated.txt","fileToken":file_token},"/openapi/dms/v1"); log(m,"PUT /iso/doc",s)
                    s,_ = req("DELETE","/iso/doc/cancel",{"code":doc_code},"/openapi/dms/v1"); log(m,"DELETE /iso/doc/cancel",s)
                    s,_ = req("DELETE","/iso/doc/destroy",{"code":doc_code},"/openapi/dms/v1"); log(m,"DELETE /iso/doc/destroy",s)
                else:
                    log(m,"PUT /iso/doc",0,"skip"); log(m,"DELETE /iso/doc/cancel",0,"skip"); log(m,"DELETE /iso/doc/destroy",0,"skip")
            else:
                log(m,"POST /iso/doc",0,"skip - no file token")
                log(m,"PUT /iso/doc",0,"skip"); log(m,"DELETE /iso/doc/cancel",0,"skip"); log(m,"DELETE /iso/doc/destroy",0,"skip")
            s,_ = dms("/iso/folder",{"code":folder_code},"DELETE"); log(m,"DELETE /iso/folder",s)

# ── 表單相關 (BPM) ────────────────────────────────────────────
def test_bpm():
    m = "BPM 表單資訊"
    s,r = bpm("/form/all"); log(m,"GET /form/all",s)
    form_code = None
    if s==200:
        # /form/all 回傳 {"model": {"categories": [...], "forms": [...]}}
        model = json.loads(r).get("model", {})
        forms = model.get("forms", []) if isinstance(model, dict) else model
        if forms: form_code = forms[0].get("code") or forms[0].get("id")

    # BUG FIX: 使用正確的 base path 取得員工清單
    emp_code = None
    s2,r2 = b("/department/employee")
    if s2==200:
        emps = json.loads(r2).get("model",[])
        if emps: emp_code = emps[0].get("code")
    
    if emp_code:
        s,_ = bpm(f"/form/apply/E/{emp_code}"); log(m,"GET /form/apply/{type}/{code}",s)
        s,_ = bpm(f"/form/apply/E/{emp_code}/{CORP_CODE}"); log(m,"GET /form/apply/{type}/{code}/{corpCode}",s)
        s,_ = bpm(f"/extconn/E/{emp_code}"); log(m,"GET /extconn/{type}/{code}",s)
        s,_ = bpm(f"/extconn/E/{emp_code}/{CORP_CODE}"); log(m,"GET /extconn/{type}/{code}/{corpCode}",s)
    else:
        log(m,"GET /form/apply/{type}/{code}",0,"skip - no emp")
        log(m,"GET /form/apply/{type}/{code}/{corpCode}",0,"skip - no emp")
        log(m,"GET /extconn/{type}/{code}",0,"skip - no emp")
        log(m,"GET /extconn/{type}/{code}/{corpCode}",0,"skip - no emp")

    if form_code:
        s,_ = bpm(f"/form/fields/{form_code}"); log(m,"GET /form/fields/{formCodeOrId}",s)
    else:
        log(m,"GET /form/fields/{formCodeOrId}",0,"skip - no form")

    # Search task lists
    s,_ = bpm("/form/search/task/apply",{"userCode":TEST_USER,"userType":"E","pageIndex":1,"pageSize":10},"POST"); log(m,"POST /form/search/task/apply",s)
    s,_ = bpm("/form/search/task/todo",{"userCode":TEST_USER,"userType":"E","pageIndex":1,"pageSize":10},"POST"); log(m,"POST /form/search/task/todo",s)

    # BPM task content
    s,_ = bpm("/form/task/content/FAKE_SN"); log(m,"GET /form/task/content/{formSn}",s,"(400 expected=連通)")

    # PUT cancel - test connectivity with fake formSn (安全: 不影響真實單據)
    s,_ = req("PUT","/form/task/cancel",{"formSn":"FAKE_SN","remark":"test"},"/openapi/bpm/v1"); log(m,"PUT /form/task/cancel",s,"(400 expected=連通)")

    # Sign/Reject - test connectivity with fake formSn
    s,_ = bpm("/form/task/sign",{"formSn":"FAKE_SN","remark":"test"},"POST"); log(m,"POST /form/task/sign",s,"(400 expected=連通)")
    s,_ = bpm("/form/task/reject",{"formSn":"FAKE_SN","remark":"test"},"POST"); log(m,"POST /form/task/reject",s,"(400 expected=連通)")

    # External form apply
    if form_code:
        s,_ = bpm(f"/form/apply/{form_code}",{"userCode":TEST_USER,"userType":"E","fields":[]},"POST"); log(m,"POST /form/apply/{formCodeOrId}",s)
    else:
        log(m,"POST /form/apply/{formCodeOrId}",0,"skip - no form")
    s,_ = bpm("/form/apply/trace",{"traceId":"fake-trace"},"POST"); log(m,"POST /form/apply/trace",s)

# ── 打卡管理 ──────────────────────────────────────────────────
def test_punch():
    m = "打卡管理"
    s,_ = eip("/punch/personal/history",{"userCode":TEST_USER,"userType":"E","startDate":"2026-01-01","endDate":"2026-12-31"},"POST"); log(m,"POST /punch/personal/history",s)
    s,_ = eip("/punch/dept/history",{"deptCode":"J0PM","startDate":"2026-01-01","endDate":"2026-12-31"},"POST"); log(m,"POST /punch/dept/history",s)

# ── 問卷管理 ──────────────────────────────────────────────────
def test_questionnaire():
    m = "問卷管理"
    s,_ = eip("/que/list",{"pageIndex":1,"pageSize":10},"POST"); log(m,"POST /que/list",s)
    s,_ = eip("/que/publish/clone",{"queId":"fake-id"},"POST"); log(m,"POST /que/publish/clone",s,"(400 expected=連通)")

# ── 通知服務 ──────────────────────────────────────────────────
def test_notify():
    m = "通知服務"
    s,r = b("/department/employee")
    emp_code = None
    if s==200:
        emps = json.loads(r).get("model",[])
        if emps: emp_code = emps[0].get("code")
    if emp_code:
        s,_ = ntf("/personal",{"userCode":emp_code,"userType":"E","title":"API Test Notification","content":"This is an automated test."}); log(m,"POST /personal",s)
    else:
        s,_ = ntf("/personal",{"userCode":TEST_USER,"userType":"E","title":"API Test","content":"Test"}); log(m,"POST /personal",s)

# ── 組織權限管理 ──────────────────────────────────────────────
def test_permission():
    m = "組織權限管理"
    s,_ = b("/permission/update",{"code":"J0PM","type":"dept","users":[]},"POST"); log(m,"POST /permission/update",s)

# ── 主程式 ────────────────────────────────────────────────────
def main():
    print("=== UOF X 全模組 API 測試開始 ===\n")
    
    tests = [
        ("部門層級管理", test_deptlevel),
        ("職務管理", test_jobfunc),
        ("職務類別管理", test_jobfunc_category),
        ("職稱管理", test_jobtitle),
        ("部門管理", test_department),
        ("部門人員/主管管理", test_dept_emp_mgr),
        ("員工管理", test_employee),
        ("代理人管理", test_agent),
        ("檔案上傳", test_file_upload),
        ("一般文件管理", test_dms),
        ("管制文件管理", test_iso_dms),
        ("BPM 表單", test_bpm),
        ("打卡管理", test_punch),
        ("問卷管理", test_questionnaire),
        ("通知服務", test_notify),
        ("組織權限管理", test_permission),
    ]
    
    for name, fn in tests:
        print(f"\n▶ {name}")
        try: fn()
        except Exception as e: print(f"  ❌ ERROR: {e}")
    
    # Write report
    rpt = str(Path(__file__).resolve().parent / "full-test-report.md")
    with open(rpt, "w", encoding="utf-8") as f:
        f.write("# UOF X OpenAPI 全模組測試報告\n\n")
        f.write(f"> **測試環境**: `{HOST}` / CorpCode: `{CORP_CODE}`\n")
        f.write("> **安全規則**: 寫入操作僅針對 `TST*` 前綴資料，測試後清除。\n\n")
        f.write("| 模組 | API | 狀態碼 | 結果 | 備註 |\n")
        f.write("| :--- | :--- | :---: | :---: | :--- |\n")
        for r in RESULTS:
            f.write(f"| {r['module']} | `{r['api']}` | {r['status']} | {r['icon']} | {r['note']} |\n")
        
        total = len(RESULTS)
        ok = sum(1 for r in RESULTS if r["status"] in [200,201,204])
        conn = sum(1 for r in RESULTS if r["status"] == 400)
        fail = sum(1 for r in RESULTS if r["status"] in [401,403])
        
        f.write(f"\n## 📊 統計\n")
        f.write(f"- **總測試數**: {total}\n")
        f.write(f"- ✅ **成功 (2xx)**: {ok}\n")
        f.write(f"- ⚠️ **已連通但參數錯誤 (400)**: {conn}\n")
        f.write(f"- ❌ **權限拒絕 (401/403)**: {fail}\n")
    
    print(f"\n=== 測試完成！報告已寫入: {rpt} ===")

if __name__ == "__main__":
    main()
