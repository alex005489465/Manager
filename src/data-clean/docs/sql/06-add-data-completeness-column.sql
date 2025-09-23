-- =====================================================
-- Manager專案 - 新增資料完整度標記欄位
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (可使用 manager_reviews_user 執行)
-- 前置條件：需先執行 01-05 的建表腳本
-- =====================================================

-- 切換到專案資料庫
USE manager_reviews_db;

-- =====================================================
-- 新增資料完整度欄位到 extracted_food_items 表
-- =====================================================

-- 為 extracted_food_items 表新增資料完整度標記欄位
ALTER TABLE extracted_food_items
ADD COLUMN data_completeness ENUM('complete', 'partial', 'minimal') DEFAULT 'partial'
COMMENT '資料完整度標記（complete=店家+料理+描述完整, partial=部分資訊, minimal=僅描述性內容）'
AFTER rating_sentiment;

-- 為保持彈性，description 欄位維持可為 NULL
-- 資料完整性由應用程式層控制，資料庫不強制約束

-- =====================================================
-- 建立新欄位的效能優化索引
-- =====================================================

-- 針對資料完整度建立索引
CREATE INDEX idx_extracted_food_completeness ON extracted_food_items(data_completeness)
COMMENT '基於資料完整度的篩選索引';

-- 複合索引：完整度與情感傾向
CREATE INDEX idx_extracted_food_completeness_sentiment ON extracted_food_items(data_completeness, rating_sentiment)
COMMENT '基於完整度和情感傾向的複合索引';

-- =====================================================
-- 驗證欄位新增結果
-- =====================================================

-- 檢查 extracted_food_items 表結構（應包含新增的欄位）
DESCRIBE extracted_food_items;

-- 檢查索引建立情況
SHOW INDEX FROM extracted_food_items;

-- 檢查新欄位的資料分布（應該都是 partial）
SELECT
    data_completeness,
    COUNT(*) as count
FROM extracted_food_items
GROUP BY data_completeness;

-- =====================================================
-- 資料完整度分類說明
-- =====================================================

-- complete: 同時具有店家名稱、料理名稱和描述
-- partial: 具有店家名稱或料理名稱其一，加上描述
-- minimal: 僅有描述性內容，無具體店家或料理名稱

-- =====================================================
-- 常用查詢範例
-- =====================================================

-- 查詢不同完整度的資料分布
/*
SELECT
    data_completeness,
    COUNT(*) as total_count,
    COUNT(dish_name) as has_dish_count,
    COUNT(vendor_name) as has_vendor_count,
    COUNT(price) as has_price_count
FROM extracted_food_items
GROUP BY data_completeness
ORDER BY total_count DESC;
*/

-- 查詢完整度最高的評價資料
/*
SELECT
    dish_name,
    vendor_name,
    description,
    price,
    rating_sentiment,
    data_completeness
FROM extracted_food_items
WHERE data_completeness = 'complete'
    AND rating_sentiment = 'positive'
ORDER BY extracted_at DESC
LIMIT 10;
*/

-- 查詢特定完整度的料理統計
/*
SELECT
    dish_name,
    COUNT(*) as mention_count,
    data_completeness
FROM extracted_food_items
WHERE dish_name IS NOT NULL
    AND data_completeness IN ('complete', 'partial')
GROUP BY dish_name, data_completeness
ORDER BY mention_count DESC;
*/

-- =====================================================
-- 回滾腳本（如需移除欄位時使用）
-- =====================================================

-- 移除相關索引和欄位的腳本（註解狀態）
/*
-- 移除索引
DROP INDEX idx_extracted_food_completeness ON extracted_food_items;
DROP INDEX idx_extracted_food_completeness_sentiment ON extracted_food_items;

-- 無需還原 description 欄位，因為未修改其屬性

-- 移除新增的欄位
ALTER TABLE extracted_food_items DROP COLUMN data_completeness;
*/