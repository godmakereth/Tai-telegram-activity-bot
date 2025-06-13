import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from database.db import Database
from handlers.activity_handler import ActivityHandler
from handlers.statistics_handler import StatisticsHandler

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    # 檢查環境變數
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("未設置 TELEGRAM_TOKEN 環境變數")
        return

    # 初始化資料庫
    db = Database()
    await db.create_tables()
    
    # 初始化處理器
    activity_handler = ActivityHandler(db)
    statistics_handler = StatisticsHandler(db)
    
    # 創建應用程式
    application = Application.builder().token(token).build()
    
    # 註冊命令處理器
    application.add_handler(CommandHandler("start", activity_handler.handle_start))
    application.add_handler(CommandHandler("stop", activity_handler.handle_stop))
    application.add_handler(CommandHandler("statistics", statistics_handler.handle_statistics))
    
    # 註冊回調處理器
    application.add_handler(CallbackQueryHandler(activity_handler.handle_callback, pattern="^start_"))
    application.add_handler(CallbackQueryHandler(statistics_handler.handle_callback, pattern="^(stats_|back)"))
    
    # 啟動機器人
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 