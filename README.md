# Telegram 活動追蹤機器人

這是一個用於追蹤群組成員活動的 Telegram 機器人，支援中文和泰文。機器人可以追蹤多種活動，並提供詳細的統計資料。

## 功能特點

- 支援多種活動追蹤：
  - 上廁所（限制時間：6分鐘）
  - 抽菸（限制時間：5分鐘）
  - 大便10（限制時間：10分鐘）
  - 大便15（限制時間：15分鐘）
  - 使用手機（限制時間：10分鐘）

- 活動管理功能：
  - 開始活動（/start）
  - 結束活動（/stop）
  - 自動計算活動時長
  - 超時提醒

- 統計功能：
  - 本日統計
  - 昨日統計
  - 本週統計
  - 上週統計
  - 本月統計
  - 上月統計

- 多語言支援：
  - 中文
  - 泰文

- 群組獨立統計：
  - 每個群組的統計資料獨立計算
  - 不同群組的活動互不影響

## 系統需求

- Python 3.7 或更高版本
- SQLite 3
- 網路連接

## 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/godmakereth/Tai-telegram-activity-bot.git
cd Tai-telegram-activity-bot
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 設置環境變數：
   - 複製 `.env.example` 為 `.env`
   - 在 `.env` 中設置您的 Telegram Bot Token
   ```bash
   cp .env.example .env
   ```
   - 編輯 `.env` 文件，填入您的 Bot Token：
   ```
   TELEGRAM_TOKEN=your_bot_token_here
   ```

4. 運行機器人：
```bash
python src/main.py
```

## Mac 與 Windows 安裝差異

| 步驟         | Mac 指令/方式                        | Windows 指令/方式                  |
|--------------|--------------------------------------|------------------------------------|
| 複製檔案     | cp .env.example .env                 | copy .env.example .env             |
| 編輯檔案     | nano .env / vim .env / open -e .env  | notepad .env                       |
| 安裝 Python  | 建議用 Homebrew 安裝最新版           | 從 python.org 下載安裝             |
| 終端機/命令  | Terminal (預設 bash/zsh)             | 命令提示字元(cmd) 或 PowerShell    |
| pip 指令     | pip 或 pip3                          | pip 或 pip3                        |

**注意事項：**
- Windows 若遇權限問題，請用「以系統管理員身分執行」命令提示字元。
- 其餘安裝與啟動步驟皆相同。

## 使用說明

1. 在 Telegram 中將機器人加入群組
2. 使用以下命令：
   - `/start` - 開始追蹤活動
   - `/stop` - 停止追蹤活動
   - `/statistics` - 查看活動統計

## 專案結構

```
.
├── src/                    # 主要程式碼資料夾
│   ├── database/          # 資料庫相關模組
│   │   └── db.py         # 資料庫操作核心
│   │
│   ├── handlers/         # 命令處理器模組
│   │   ├── activity_handler.py    # 活動處理
│   │   └── statistics_handler.py  # 統計處理
│   │
│   ├── utils/            # 工具函數模組
│   │   ├── config.py     # 配置管理
│   │   └── helpers.py    # 輔助函數
│   │
│   └── main.py          # 主程式入口
│
├── .env                  # 環境變數設定檔
├── .env.example         # 環境變數範本
├── requirements.txt     # 依賴套件清單
└── README.md           # 專案說明文件
```

## 模組說明

1. **資料庫模組 (database/db.py)**
   - 處理所有資料庫操作
   - 管理活動記錄
   - 提供統計查詢功能

2. **活動處理器 (handlers/activity_handler.py)**
   - 處理活動相關命令
   - 管理活動開始和結束
   - 計算活動時長

3. **統計處理器 (handlers/statistics_handler.py)**
   - 處理統計相關命令
   - 生成統計報表
   - 管理時間範圍選擇

4. **配置模組 (utils/config.py)**
   - 管理活動限制時間
   - 設定表情符號
   - 定義按鈕文字

5. **工具函數 (utils/helpers.py)**
   - 時間計算功能
   - 格式化輸出
   - 通用輔助函數

## 資料庫結構

1. **activities 表**
   - 記錄所有已完成的活動
   - 包含：使用者ID、群組ID、活動類型、開始時間、結束時間、持續時間、超時時間等

2. **ongoing 表**
   - 記錄當前進行中的活動
   - 包含：使用者ID、群組ID、活動類型、開始時間等

## 注意事項

1. 請確保機器人具有以下權限：
   - 發送訊息
   - 讀取訊息
   - 使用內聯鍵盤

2. 資料庫檔案 (tracker.db) 會自動創建在專案根目錄

3. 建議定期備份資料庫檔案

## 常見問題

1. Q: 如何重置統計資料？
   A: 刪除 tracker.db 檔案，系統會自動重新創建

2. Q: 如何修改活動時間限制？
   A: 在 src/utils/config.py 中修改 ACTIVITY_LIMITS 設定

3. Q: 如何添加新的活動類型？
   A: 在 src/utils/config.py 中添加新的活動設定

## 聯絡方式

如有問題或建議，請提交 Issue 或 Pull Request。 