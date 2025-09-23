# Manager 專案 - 評論資料清理與分析

這個資料夾包含永大夜市評論資料的清理、匯入和分析工具。

## 🚀 快速開始

### 環境設定
```bash
# 1. 安裝依賴套件
pip install mysql-connector-python python-dotenv google-generativeai

# 2. 設定環境變數（複製 .env.example 為 .env）
cp .env.example .env
# 編輯 .env 填入 GEMINI_API_KEY 和資料庫密碼
```

### 資料庫準備
```bash
# 執行 SQL 腳本建立資料庫和表格
# 在 phpMyAdmin 中依序執行：
# 1. docs/sql/01-database-user-setup.sql
# 2. docs/sql/02-create-tables.sql
# 3. docs/sql/03-create-review-filter-table.sql
# 4. docs/sql/04-add-specific-food-column.sql
# 5. docs/sql/05-create-extracted-food-items-table.sql
# 6. docs/sql/06-add-data-completeness-column.sql
```

## 📜 腳本說明

### 1. import_data.py
**用途**: 將原始 JSON 評論資料匯入 MySQL 資料庫
```bash
python import_data.py
```
- 讀取 `./data/raw/` 目錄下的 JSON 檔案
- 匯入到 `reviews` 和 `search_metadata` 表
- 自動處理日期格式轉換和資料清理

### 2. food_relevance_checker.py
**用途**: 使用 AI 判別評論是否與食物相關
```bash
python food_relevance_checker.py
```
- 分析 `review_analysis` 表中的評論內容
- 使用 Gemini API 批次判別食物相關性
- 更新 `is_project_related` 欄位 (TRUE=食物相關, FALSE=非食物相關)

### 3. specific_food_analyzer.py
**用途**: 進階分析食物相關評論是否提到具體食物項目
```bash
python specific_food_analyzer.py
```
- 處理已標記為食物相關的評論
- 判別是否提到具體料理名稱、店家等
- 更新 `has_specific_food_mention` 欄位 (TRUE=具體提及, FALSE=泛指)

### 4. extract_food_items.py
**用途**: 將具體食物評論結構化提取為可分析的資料項目
```bash
python extract_food_items.py
```
- 使用 Gemini 2.5 Flash-Lite 模型分析具體食物評論
- 提取料理名稱、店家名稱、描述、價格、情感評價等結構化資料
- 儲存到 `extracted_food_items` 表，支援一對多關係（一則評論可提取多個項目）
- 自動標記資料完整度 (complete/partial/minimal)

### 5. export_specific_food_content.py
**用途**: 匯出具體食物評論內容到 Markdown 檔案
```bash
python export_specific_food_content.py
```
- 提取所有 `has_specific_food_mention = 1` 的評論內容
- 輸出為編號格式的 `specific_food_mentions.md` 檔案

## 🔍 驗證工具

### verify_data.py
檢查資料匯入結果和統計資訊
```bash
python verify_data.py
```

## 📊 處理流程
1. **資料匯入** → `import_data.py`
2. **食物相關性分析** → `food_relevance_checker.py`
3. **具體食物項目分析** → `specific_food_analyzer.py`
4. **結構化資料提取** → `extract_food_items.py`
5. **結果驗證** → `verify_data.py`

## 📁 輸出檔案
- `specific_food_mentions.md` - 具體食物評論內容（由 `export_specific_food_content.py` 產生）
- `extract_food_items.log` - 結構化提取過程日誌

## 📋 資料庫表結構
- `reviews` - 原始評論資料
- `search_metadata` - 搜尋元數據
- `review_analysis` - 評論分析結果（包含食物相關性標記）
- `extracted_food_items` - 結構化食物項目（396 個項目，涵蓋 158 則評論）

## 📖 詳細文檔
- `docs/具體食物項目分析計劃.md` - 分析計劃說明
- `docs/結構化食物資料提取記錄.md` - 提取過程記錄
- `docs/sql/` - 所有資料庫建立和修改腳本

詳細說明請參考 `docs/` 目錄下的相關文檔。