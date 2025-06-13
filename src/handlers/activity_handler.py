import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database.db import Database
from ..utils.config import ACTIVITY_LIMITS, ACTIVITY_EMOJIS, BUTTONS
from ..utils.helpers import format_duration

logger = logging.getLogger(__name__)

class ActivityHandler:
    def __init__(self, db: Database):
        self.db = db

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理開始活動命令"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # 檢查是否已有進行中的活動
        ongoing = await self.db.get_ongoing_activity(user.id, chat_id)
        if ongoing:
            await update.message.reply_text(
                f"您已經有一個進行中的活動：{ongoing['activity']}\n"
                f"開始時間：{ongoing['start_time']}"
            )
            return

        # 創建活動選單
        keyboard = [
            [InlineKeyboardButton(activity, callback_data=f"start_{activity}")]
            for activity in ACTIVITY_LIMITS.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "請選擇要開始的活動/กรุณาเลือกกิจกรรม:",
            reply_markup=reply_markup
        )

    async def handle_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理停止活動命令"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # 檢查是否有進行中的活動
        ongoing = await self.db.get_ongoing_activity(user.id, chat_id)
        if not ongoing:
            await update.message.reply_text("您目前沒有進行中的活動/คุณไม่มีกิจกรรมที่กำลังดำเนินการอยู่")
            return

        # 停止活動
        result = await self.db.stop_activity(user.id, chat_id, ACTIVITY_LIMITS)
        if not result:
            await update.message.reply_text("停止活動時發生錯誤/เกิดข้อผิดพลาดในการหยุดกิจกรรม")
            return
        
        activity = result['activity']
        start_time = datetime.fromisoformat(result['start_time'])
        end_time = datetime.fromisoformat(result['end_time'])
        duration = result['duration']
        overtime = result['overtime']
        
        emoji = ACTIVITY_EMOJIS.get(activity, '')
        duration_str = format_duration(duration)
        overtime_str = format_duration(overtime) if overtime > 0 else "無/ไม่มี"
        
        await update.message.reply_text(
            f"{emoji} {activity} 結束/จบ\n"
            f"開始時間/เวลาเริ่ม: {start_time.strftime('%H:%M:%S')}\n"
            f"結束時間/เวลาจบ: {end_time.strftime('%H:%M:%S')}\n"
            f"持續時間/ระยะเวลา: {duration_str}\n"
            f"超時時間/เวลาเกิน: {overtime_str}"
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理回調查詢"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("start_"):
            activity = query.data[6:]
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            # 開始活動
            start_time = datetime.now()
            await self.db.start_activity(
                user.id,
                chat_id,
                activity,
                start_time,
                user.full_name
            )
            
            emoji = ACTIVITY_EMOJIS.get(activity, '')
            limit = format_duration(ACTIVITY_LIMITS[activity])
            
            await query.edit_message_text(
                f"{emoji} {activity} 開始/เริ่ม\n"
                f"開始時間/เวลาเริ่ม: {start_time.strftime('%H:%M:%S')}\n"
                f"限制時間/เวลาจำกัด: {limit}"
            ) 