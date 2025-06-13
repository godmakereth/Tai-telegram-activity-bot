import logging
import aiosqlite
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = 'tracker.db'):
        self.db_path = db_path

    async def create_tables(self):
        """創建資料庫和必要的表"""
        async with aiosqlite.connect(self.db_path) as db:
            # 檢查表是否存在
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activities'") as cursor:
                activities_exists = await cursor.fetchone() is not None
                
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ongoing'") as cursor:
                ongoing_exists = await cursor.fetchone() is not None
            
            # 如果表不存在才創建
            if not activities_exists:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        activity TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP NOT NULL,
                        duration INTEGER NOT NULL,
                        overtime INTEGER NOT NULL,
                        user_full_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                logger.info("Created activities table")
            
            if not ongoing_exists:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS ongoing (
                        user_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        activity TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        user_full_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, chat_id)
                    )
                ''')
                logger.info("Created ongoing table")
            
            await db.commit()

    async def get_ongoing_activity(self, user_id: int, chat_id: int) -> Optional[Dict]:
        """獲取使用者正在進行的活動"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT activity, start_time FROM ongoing WHERE user_id = ? AND chat_id = ?',
                (user_id, chat_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'activity': row[0],
                        'start_time': datetime.fromisoformat(row[1])
                    }
                return None

    async def start_activity(self, user_id: int, chat_id: int, activity: str, user_full_name: str):
        """開始一個新的活動"""
        start_time = datetime.now()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO ongoing (user_id, chat_id, activity, start_time, user_full_name) VALUES (?, ?, ?, ?, ?)',
                (user_id, chat_id, activity, start_time.isoformat(), user_full_name)
            )
            await db.commit()

    async def stop_activity(self, user_id: int, chat_id: int, activity_limits: Dict[str, int]) -> Optional[Dict]:
        """停止當前活動並返回活動詳情"""
        async with aiosqlite.connect(self.db_path) as db:
            # 獲取活動信息
            async with db.execute(
                'SELECT activity, start_time, user_full_name FROM ongoing WHERE user_id = ? AND chat_id = ?',
                (user_id, chat_id)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                activity = row[0]
                start_time = datetime.fromisoformat(row[1])
                user_full_name = row[2]
                end_time = datetime.now()
                duration = int((end_time - start_time).total_seconds())
                
                # 計算超時時間
                activity_limit = activity_limits.get(activity, 5 * 60)  # 預設5分鐘
                overtime = max(0, duration - activity_limit)
                
                # 插入活動記錄
                await db.execute('''
                    INSERT INTO activities 
                    (user_id, chat_id, activity, start_time, end_time, duration, overtime, user_full_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, chat_id, activity, 
                    start_time.isoformat(), end_time.isoformat(),
                    duration, overtime, user_full_name
                ))
                
                # 刪除進行中的活動
                await db.execute(
                    'DELETE FROM ongoing WHERE user_id = ? AND chat_id = ?',
                    (user_id, chat_id)
                )
                
                await db.commit()
                
                return {
                    'activity': activity,
                    'duration': duration,
                    'overtime': overtime,
                    'user_full_name': user_full_name,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }

    async def get_detailed_records(self, time_range: str, chat_id: int, activity_limits: Dict[str, int]) -> List[Dict]:
        """獲取指定時間範圍的詳細記錄"""
        async with aiosqlite.connect(self.db_path) as db:
            # 根據時間範圍構建 SQL 條件
            time_condition = ""
            if time_range == "today":
                time_condition = "AND date(start_time) = date('now', 'localtime')"
            elif time_range == "yesterday":
                time_condition = "AND date(start_time) = date('now', 'localtime', '-1 day')"
            elif time_range == "this_week":
                time_condition = "AND strftime('%Y-%W', start_time) = strftime('%Y-%W', 'now', 'localtime')"
            elif time_range == "last_week":
                time_condition = "AND strftime('%Y-%W', start_time) = strftime('%Y-%W', 'now', 'localtime', '-7 days')"
            elif time_range == "this_month":
                time_condition = "AND strftime('%Y-%m', start_time) = strftime('%Y-%m', 'now', 'localtime')"
            elif time_range == "last_month":
                time_condition = "AND strftime('%Y-%m', start_time) = strftime('%Y-%m', 'now', 'localtime', '-1 month')"

            # 構建活動限制條件
            activity_limits_sql = "CASE activity\n"
            for activity, limit in activity_limits.items():
                activity_limits_sql += f"    WHEN '{activity}' THEN {limit}\n"
            activity_limits_sql += "    ELSE 300 END"

            # 執行查詢
            query = f"""
                WITH activity_stats AS (
                    SELECT 
                        user_full_name,
                        activity,
                        COUNT(*) as count,
                        SUM(duration) as total_duration,
                        SUM(CASE 
                            WHEN duration > {activity_limits_sql}
                            THEN duration - {activity_limits_sql}
                            ELSE 0 
                        END) as total_overtime,
                        COUNT(CASE 
                            WHEN duration > {activity_limits_sql}
                            THEN 1 
                            ELSE NULL 
                        END) as overtime_count
                    FROM activities 
                    WHERE chat_id = ? {time_condition}
                    GROUP BY user_full_name, activity
                )
                SELECT 
                    user_full_name,
                    activity,
                    count,
                    total_duration,
                    total_overtime,
                    overtime_count
                FROM activity_stats
                ORDER BY user_full_name, activity
            """
            
            async with db.execute(query, (chat_id,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'user_full_name': row[0],
                        'activity': row[1],
                        'count': row[2],
                        'total_duration': row[3],
                        'total_overtime': row[4],
                        'overtime_count': row[5]
                    }
                    for row in rows
                ] 