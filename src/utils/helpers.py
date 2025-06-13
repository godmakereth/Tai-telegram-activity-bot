from datetime import datetime, timedelta
from typing import Tuple, Dict, List
from .config import TIME_RANGES

def get_time_range(range_type: str) -> Tuple[datetime, datetime]:
    """根據時間範圍類型獲取開始和結束時間"""
    now = datetime.now()
    
    if range_type == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == 'yesterday':
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59)
    elif range_type == 'this_week':
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == 'last_week':
        start = (now - timedelta(days=now.weekday() + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (now - timedelta(days=now.weekday() + 1)).replace(hour=23, minute=59, second=59)
    elif range_type == 'this_month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == 'last_month':
        if now.month == 1:
            start = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (now.replace(day=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)
    else:
        raise ValueError(f"Invalid range type: {range_type}")
    
    return start, end

def format_duration(seconds: int) -> str:
    """將秒數轉換為時分秒格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}小時{minutes}分{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分{seconds}秒"
    else:
        return f"{seconds}秒"

def format_statistics(records: List[Dict]) -> str:
    """格式化統計資料"""
    if not records:
        return "無資料/ไม่มีข้อมูล"
    
    result = []
    for record in records:
        activity = record['activity']
        total_duration = format_duration(record['total_duration'])
        total_overtime = format_duration(record['total_overtime'])
        count = record['count']
        
        result.append(
            f"活動/กิจกรรม: {activity}\n"
            f"次數/ครั้ง: {count}\n"
            f"總時長/เวลารวม: {total_duration}\n"
            f"總超時/เวลาเกิน: {total_overtime}\n"
        )
    
    return "\n".join(result) 