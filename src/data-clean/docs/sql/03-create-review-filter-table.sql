-- =====================================================
-- Manager專案 - 評論內容篩選表建立腳本
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (可使用 manager_reviews_user 執行)
-- 前置條件：需先執行 01-database-user-setup.sql 和 02-create-tables.sql
-- =====================================================

-- 切換到專案資料庫
USE manager_reviews_db;

-- =====================================================
-- 建立 review_analysis 表 - 評論分析
-- =====================================================
CREATE TABLE review_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '統一自增主鍵',
    review_id BIGINT COMMENT '關聯原reviews表的id',
    content TEXT COMMENT '評論內容（複製自reviews.snippet）',
    is_project_related BOOLEAN DEFAULT NULL COMMENT '是否跟專案相關（NULL=未判別, TRUE=相關, FALSE=不相關）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='評論分析表 - 存儲有內容的評論及專案相關性標示';

-- =====================================================
-- 建立效能優化索引
-- =====================================================

-- 針對 review_id 建立索引（關聯查詢用）
CREATE INDEX idx_review_analysis_review_id ON review_analysis(review_id)
COMMENT '基於review_id的關聯查詢索引';

-- 針對 is_project_related 建立索引（篩選查詢用）
CREATE INDEX idx_review_analysis_project_related ON review_analysis(is_project_related)
COMMENT '基於專案相關性的篩選索引';

-- 針對 created_at 建立索引（時間排序用）
CREATE INDEX idx_review_analysis_created_at ON review_analysis(created_at)
COMMENT '基於建立時間的排序索引';

-- =====================================================
-- 匯入有內容的評論資料
-- =====================================================

-- 將reviews表中有內容的評論匯入到分析表
INSERT INTO review_analysis (review_id, content)
SELECT
    id,
    snippet
FROM reviews
WHERE snippet IS NOT NULL
    AND snippet != ''
    AND TRIM(snippet) != '';

-- =====================================================
-- 驗證資料匯入結果
-- =====================================================

-- 檢查匯入的記錄數
SELECT COUNT(*) as '有內容評論數量' FROM review_analysis;

-- 檢查專案相關性分布（應該全為NULL）
SELECT
    is_project_related,
    COUNT(*) as count
FROM review_analysis
GROUP BY is_project_related;

-- 顯示部分資料樣本
SELECT
    id,
    review_id,
    LEFT(content, 100) as content_preview,
    is_project_related,
    created_at
FROM review_analysis
ORDER BY created_at DESC
LIMIT 5;