import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database.db import Database
from ..utils.config import TIME_RANGES, BUTTONS, ACTIVITY_LIMITS
from ..utils.helpers import get_time_range, format_statistics

logger = logging.getLogger(__name__)

class StatisticsHandler:
    def __init__(self, db: Database):
        self.db = db

    async def handle_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理統計命令"""
        keyboard = [
            [InlineKeyboardButton(BUTTONS[range_type], callback_data=f"stats_{range_type}")]
            for range_type in TIME_RANGES.keys()
        ]
        keyboard.append([InlineKeyboardButton(BUTTONS['back'], callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "請選擇要查看的時間範圍/กรุณาเลือกช่วงเวลา:",
            reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理回調查詢"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "back":
            await self.handle_statistics(update, context)
            return
            
        if query.data.startswith("stats_"):
            range_type = query.data[6:]
            chat_id = update.effective_chat.id
            
            # 獲取統計資料
            records = await self.db.get_detailed_records(range_type, chat_id, ACTIVITY_LIMITS)
            
            # 格式化並發送結果
            range_name = TIME_RANGES[range_type][0]
            result = f"{range_name}統計資料/สถิติ{range_name}:\n\n{format_statistics(records)}"
            
            await query.edit_message_text(result) 