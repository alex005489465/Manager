-- =====================================================
-- Manager專案 - 結構化食物資料提取表建立腳本
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (可使用 manager_reviews_user 執行)
-- 前置條件：需先執行 01-database-user-setup.sql、02-create-tables.sql、03-create-review-filter-table.sql、04-add-specific-food-column.sql
-- =====================================================

-- 切換到專案資料庫
USE manager_reviews_db;

-- =====================================================
-- 新增處理狀態欄位到 review_analysis 表
-- =====================================================

-- 為 review_analysis 表新增提取狀態欄位
ALTER TABLE review_analysis
ADD COLUMN is_food_items_extracted BOOLEAN DEFAULT FALSE
COMMENT '是否已提取結構化食物資料（FALSE=未處理, TRUE=已處理）'
AFTER has_specific_food_mention;

-- =====================================================
-- 建立 extracted_food_items 表 - 結構化食物項目
-- =====================================================

CREATE TABLE extracted_food_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '統一自增主鍵',
    review_id BIGINT NOT NULL COMMENT '關聯review_analysis表的id',
    dish_name VARCHAR(100) COMMENT '料理名稱（如：臭豆腐、蚵仔煎）',
    vendor_name VARCHAR(100) COMMENT '店家攤位名稱（如：326臭臭鍋）',
    description TEXT COMMENT '口味食材體驗描述',
    price VARCHAR(50) COMMENT '價格資訊（如有提及）',
    rating_sentiment ENUM('positive', 'negative', 'neutral') COMMENT '評價情感傾向',
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '提取時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='結構化食物項目表 - 從評論中提取的具體食物資訊';

-- =====================================================
-- 建立效能優化索引
-- =====================================================

-- 針對 review_analysis 表的新欄位建立索引
CREATE INDEX idx_review_analysis_extracted ON review_analysis(is_food_items_extracted)
COMMENT '基於提取狀態的篩選索引';

-- 複合索引：用於查找待處理的具體食物評論
CREATE INDEX idx_review_analysis_extract_target ON review_analysis(has_specific_food_mention, is_food_items_extracted)
COMMENT '基於食物提及和提取狀態的複合索引';

-- 針對 extracted_food_items 表的常用查詢欄位建立索引
CREATE INDEX idx_extracted_food_review_id ON extracted_food_items(review_id)
COMMENT '基於review_id的關聯查詢索引';

CREATE INDEX idx_extracted_food_dish_name ON extracted_food_items(dish_name)
COMMENT '基於料理名稱的查詢索引';

CREATE INDEX idx_extracted_food_vendor_name ON extracted_food_items(vendor_name)
COMMENT '基於店家名稱的查詢索引';

CREATE INDEX idx_extracted_food_sentiment ON extracted_food_items(rating_sentiment)
COMMENT '基於評價情感的篩選索引';

-- =====================================================
-- 驗證表建立結果
-- =====================================================

-- 檢查 review_analysis 表結構（應包含新增的欄位）
DESCRIBE review_analysis;

-- 檢查 extracted_food_items 表結構
DESCRIBE extracted_food_items;

-- 檢查索引建立情況
SHOW INDEX FROM review_analysis;
SHOW INDEX FROM extracted_food_items;

-- 檢查待處理的評論數量
SELECT COUNT(*) as '待處理的具體食物評論數量'
FROM review_analysis
WHERE has_specific_food_mention = TRUE
    AND is_food_items_extracted = FALSE;

-- =====================================================
-- 常用查詢範例
-- =====================================================

-- 查詢待處理的評論（供腳本使用）
/*
SELECT id, content
FROM review_analysis
WHERE has_specific_food_mention = TRUE
    AND is_food_items_extracted = FALSE
ORDER BY id
LIMIT 20;
*/

-- 查詢某則評論提取的所有食物項目
/*
SELECT
    e.dish_name,
    e.vendor_name,
    e.description,
    e.price,
    e.rating_sentiment
FROM extracted_food_items e
WHERE e.review_id = 1;
*/

-- 統計最受歡迎的料理
/*
SELECT
    dish_name,
    COUNT(*) as mention_count,
    SUM(CASE WHEN rating_sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN rating_sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count
FROM extracted_food_items
WHERE dish_name IS NOT NULL
GROUP BY dish_name
ORDER BY mention_count DESC
LIMIT 20;
*/

-- 統計店家評價分布
/*
SELECT
    vendor_name,
    COUNT(*) as total_mentions,
    SUM(CASE WHEN rating_sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
    SUM(CASE WHEN rating_sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral,
    SUM(CASE WHEN rating_sentiment = 'negative' THEN 1 ELSE 0 END) as negative
FROM extracted_food_items
WHERE vendor_name IS NOT NULL
GROUP BY vendor_name
ORDER BY total_mentions DESC;
*/

-- =====================================================
-- 回滾腳本（如需移除時使用）
-- =====================================================

-- 移除相關資料的腳本（註解狀態）
/*
-- 移除外鍵約束和表
DROP TABLE IF EXISTS extracted_food_items;

-- 移除索引
DROP INDEX idx_review_analysis_extracted ON review_analysis;
DROP INDEX idx_review_analysis_extract_target ON review_analysis;

-- 移除新增的欄位
ALTER TABLE review_analysis DROP COLUMN is_food_items_extracted;
*/