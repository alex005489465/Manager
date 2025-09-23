-- =====================================================
-- Manager專案 - 新增具體食物項目判別欄位
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (可使用 manager_reviews_user 執行)
-- 前置條件：需先執行 01-03 的建表和資料匯入腳本
-- =====================================================

-- 切換到專案資料庫
USE manager_reviews_db;

-- =====================================================
-- 新增具體食物項目判別欄位
-- =====================================================

-- 為 review_analysis 表新增欄位（加在 is_project_related 欄位後面）
ALTER TABLE review_analysis
ADD COLUMN has_specific_food_mention BOOLEAN DEFAULT NULL
COMMENT '是否提到具體食物項目或店家（NULL=未判別, TRUE=有具體提及, FALSE=僅泛指）'
AFTER is_project_related;

-- =====================================================
-- 建立效能優化索引
-- =====================================================

-- 針對新欄位建立索引（條件查詢用）
CREATE INDEX idx_review_analysis_specific_food ON review_analysis(has_specific_food_mention)
COMMENT '基於具體食物提及的篩選索引';

-- =====================================================
-- 驗證欄位新增結果
-- =====================================================

-- 檢查表結構
DESCRIBE review_analysis;

-- 檢查索引建立情況
SHOW INDEX FROM review_analysis;

-- 檢查新欄位的資料分布（應該全為NULL）
SELECT
    has_specific_food_mention,
    COUNT(*) as count
FROM review_analysis
GROUP BY has_specific_food_mention;

-- 檢查需要處理的食物相關評論數量
SELECT COUNT(*) as '待處理的食物相關評論數量'
FROM review_analysis
WHERE is_project_related = TRUE
    AND has_specific_food_mention IS NULL;

-- =====================================================
-- 常用查詢範例
-- =====================================================

-- 查詢所有具體食物提及的評論
/*
SELECT id, LEFT(content, 100) as content_preview, has_specific_food_mention
FROM review_analysis
WHERE is_project_related = TRUE
    AND has_specific_food_mention = TRUE
ORDER BY created_at DESC;
*/

-- 統計不同類型評論的分布
/*
SELECT
    CASE
        WHEN is_project_related = FALSE THEN '非食物相關'
        WHEN is_project_related = TRUE AND has_specific_food_mention = TRUE THEN '具體食物提及'
        WHEN is_project_related = TRUE AND has_specific_food_mention = FALSE THEN '泛指食物評論'
        WHEN is_project_related = TRUE AND has_specific_food_mention IS NULL THEN '待判別食物評論'
        ELSE '其他'
    END as evaluation_type,
    COUNT(*) as count
FROM review_analysis
GROUP BY evaluation_type
ORDER BY count DESC;
*/

-- =====================================================
-- 回滾腳本（如需移除欄位時使用）
-- =====================================================

-- 移除索引和欄位的腳本（註解狀態）
/*
-- 移除索引
DROP INDEX idx_review_analysis_specific_food ON review_analysis;

-- 移除欄位
ALTER TABLE review_analysis DROP COLUMN has_specific_food_mention;
*/