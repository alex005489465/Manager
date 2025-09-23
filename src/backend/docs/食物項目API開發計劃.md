# 食物項目API開發計劃

## 📋 目標
開發單一API查詢 `extracted_food_items` 表資料

## 🎯 API需求
- **單一端點**: `GET /api/food-items`
- **功能**: 查詢所有食物項目資料
- **篩選**: 支援 `rating_sentiment` 和 `data_completeness` 篩選
- **搜尋**: 支援 `dish_name` 和 `vendor_name` 關鍵字搜尋
- **回應**: 分頁格式資料

## 🏗️ 開發任務

### 1. 多資料源配置
建立 `DatabaseConfig` 類別，配置連接 `manager_reviews_db`

### 2. 核心開發
- **實體**: `ExtractedFoodItem` - 對應資料表結構
- **存儲庫**: `ExtractedFoodItemRepository` - 資料查詢
- **服務**: `ExtractedFoodItemService` - 業務邏輯
- **控制器**: `FoodItemController` - API端點

### 3. 資料傳輸物件
- **查詢請求**: `FoodItemQueryRequest` - 接收篩選搜尋參數
- **回應資料**: `FoodItemDTO` - 單項資料格式
- **分頁回應**: `PagedResponse<FoodItemDTO>` - 分頁資料格式

### 4. 查詢參數
- `page`: 頁碼（預設 1，1-based）
- `pageSize`: 每頁數量（預設 20）
- `ratingSentiment`: 評價情感篩選（positive/negative/neutral）
- `dataCompleteness`: 資料完整度篩選（complete/partial/minimal）
- `dishName`: 料理名稱關鍵字搜尋
- `vendorName`: 店家名稱關鍵字搜尋

## 📦 預期成果
- 一個完整的分頁查詢API
- 支援多條件篩選和搜尋
- 統一的回應格式
- 符合專案架構規範