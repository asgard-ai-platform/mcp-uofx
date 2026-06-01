from ..api_client import uofx_client
from collections import defaultdict

def get_my_punch_history(user_code: str, start_date: str, end_date: str, user_type: int = 0) -> str:
    """查詢個人出勤紀錄，並指出打卡異常（遲到/早退/未打卡）"""
    payload = {
        "dateRange": {
            "since": f"{start_date}T00:00:00+08:00",
            "until": f"{end_date}T23:59:59+08:00"
        },
        "timeZoneId": "Taipei Standard Time",
        "queryPunchHistoryType": 0,
        "user": {
            "userType": user_type,
            "userCode": user_code,
            "corpCode": uofx_client.corp_code
        }
    }
    
    try:
        response = uofx_client.post("/openapi/eip/v1/punch/personal/history", payload=payload)
        
        # API 回傳個別打卡事件（每次刷卡一筆），需按日彙整
        if isinstance(response, list):
            records = response
        elif isinstance(response, dict):
            m = response.get("model", [])
            records = m if isinstance(m, list) else []
        else:
            records = []
            
        if not records:
            return f"找不到 {user_code} 在 {start_date} 到 {end_date} 期間的打卡資料。"
            
        # 按日期彙整
        daily = defaultdict(list)
        for rec in records:
            punch_dt = rec.get("punchDate", "")
            if punch_dt:
                date_part = punch_dt[:10]  # YYYY-MM-DD
                time_part = punch_dt[11:16] if len(punch_dt) > 10 else "?"
                daily[date_part].append(time_part)
        
        report_lines = []
        abnormal_count = 0
        for date in sorted(daily.keys()):
            times = daily[date]
            times_str = ", ".join(times)
            if len(times) < 2:
                status = "⚠️ 疑缺刷"
                abnormal_count += 1
            else:
                status = "✅ 正常"
            report_lines.append(f"{date} [{status}]: 共 {len(times)} 次 ({times_str})")
            
        summary = f"📊 {user_code} 打卡報告 ({start_date} ~ {end_date}): 共 {len(daily)} 天，疑缺刷 {abnormal_count} 天。\n"
        return summary + "\n".join(report_lines)
            
    except Exception as e:
        return f"❌ 查詢打卡紀錄時發生錯誤: {str(e)}"

def get_dept_punch_report(dept_code: str, start_date: str, end_date: str, include_sub: bool = False) -> str:
    """查詢部門人員的異常打卡紀錄 (為避免資料量過大，僅回傳疑缺刷名單)"""
    payload = {
        "dateRange": {
            "since": f"{start_date}T00:00:00+08:00",
            "until": f"{end_date}T23:59:59+08:00"
        },
        "timeZoneId": "Taipei Standard Time",
        "queryPunchHistoryType": 0,
        "deptCode": dept_code,
        "includeSubDept": include_sub
    }
    
    try:
        response = uofx_client.post("/openapi/eip/v1/punch/dept/history", payload=payload)
        
        # API 回傳個別打卡事件列表（每次刷卡一筆，含 account 與 punchDate）
        if isinstance(response, list):
            records = response
        else:
            m = response.get("model", [])
            records = m if isinstance(m, list) else []
            
        # 1. 嘗試取得部門員工名單做對照
        active_employees = []
        account_names = {}
        try:
            emp_response = uofx_client.get(f"/openapi/base/v1/department/employee/{dept_code}/false")
            emps = emp_response.get("model", []) if isinstance(emp_response, dict) else []
            for emp in emps:
                account = emp.get("account")
                name = emp.get("name") or emp.get("UserName") or "未知"
                if account:
                    active_employees.append((account, name))
                    account_names[account] = name
        except Exception:
            pass
            
        # 如果既沒有打卡記錄，也無法取得員工名單，才回傳無資料
        if not records and not active_employees:
            return f"找不到部門 {dept_code} 在 {start_date} 到 {end_date} 期間的打卡資料。"
            
        # 2. 彙整打卡時間
        person_daily = defaultdict(lambda: defaultdict(list))
        recorded_dates = set()
        
        for rec in records:
            account = rec.get("account", "unknown")
            punch_dt = rec.get("punchDate", "")
            if punch_dt:
                date_part = punch_dt[:10]
                time_part = punch_dt[11:16]
                person_daily[account][date_part].append(time_part)
                recorded_dates.add(date_part)
                
        # 3. 補齊工作日完全未打卡 (0次) 的人員資料
        from datetime import datetime, timedelta
        all_dates = []
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            curr = start_dt
            while curr <= end_dt:
                all_dates.append(curr)
                curr += timedelta(days=1)
        except Exception:
            pass
            
        if active_employees:
            dates_to_check = all_dates if all_dates else [datetime.strptime(d, "%Y-%m-%d") for d in recorded_dates]
            for dt in dates_to_check:
                date_str = dt.strftime("%Y-%m-%d")
                is_weekend = dt.weekday() >= 5
                
                # 週末不主動檢查未打卡的人 (除非有加班打卡事件)
                if is_weekend:
                    continue
                    
                # 平日工作日若無紀錄，補上空的打卡清單以利篩選
                for account, name in active_employees:
                    if date_str not in person_daily[account]:
                        person_daily[account][date_str] = []
                        
        # 4. 彙整疑缺刷或未打卡清單
        abnormal_lines = []
        for account in sorted(person_daily.keys()):
            name_label = f" - {account_names[account]}" if account in account_names else ""
            for date in sorted(person_daily[account].keys()):
                times = person_daily[account][date]
                if len(times) < 2:
                    if len(times) == 0:
                        abnormal_lines.append(f"- {account}{name_label} ({date}): 未打卡 (0 次)")
                    else:
                        abnormal_lines.append(f"- {account}{name_label} ({date}): 僅 {len(times)} 次打卡 ({', '.join(times)})")
        
        if not abnormal_lines:
            return f"✅ 部門 {dept_code} 在 {start_date} 到 {end_date} 期間每日打卡均達 2 次以上！"
            
        summary = f"⚠️ 部門 {dept_code} 疑似缺刷 {len(abnormal_lines)} 筆：\n"
        return summary + "\n".join(abnormal_lines)
        
    except Exception as e:
        return f"❌ 查詢部門打卡異常時發生錯誤: {str(e)}"
