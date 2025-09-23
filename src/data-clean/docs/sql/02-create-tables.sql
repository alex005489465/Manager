-- =====================================================
-- Manager專案 - 資料表結構建立腳本
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (可使用 manager_reviews_user 執行)
-- 前置條件：需先執行 01-database-user-setup.sql
-- =====================================================

-- 切換到專案資料庫
USE manager_reviews_db;

-- =====================================================
-- 建立 search_metadata 表 - 搜尋元數據
-- =====================================================
CREATE TABLE search_metadata (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '統一自增主鍵',
    search_id VARCHAR(50) COMMENT '搜尋業務識別碼',
    google_maps_reviews_url TEXT COMMENT 'Google Maps評論頁面URL',
    data_id VARCHAR(100) COMMENT 'Google Maps地點的data_id',
    title VARCHAR(200) COMMENT '地點名稱',
    address TEXT COMMENT '地點地址',
    rating DECIMAL(2,1) COMMENT '地點平均評分',
    reviews INTEGER COMMENT '評論總數'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='搜尋元數據表 - 存儲Google Maps地點基本資訊';

-- =====================================================
-- 建立 reviews 表 - 評論內容
-- =====================================================
CREATE TABLE reviews (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '統一自增主鍵',
    review_id VARCHAR(100) COMMENT '評論業務識別碼',
    search_id VARCHAR(50) COMMENT '關聯搜尋記錄的業務識別碼（無約束）',
    rating DECIMAL(2,1) COMMENT '評論評分',
    snippet TEXT COMMENT '評論文字內容',
    link TEXT COMMENT '評論連結',
    iso_date TIMESTAMP NULL COMMENT '評論發布日期',
    iso_date_of_last_edit TIMESTAMP NULL COMMENT '評論最後編輯日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='評論內容表 - 存儲Google Maps評論詳細資訊';

-- =====================================================
-- 建立效能優化索引
-- =====================================================

-- 針對 reviews 表的常用查詢欄位建立索引
CREATE INDEX idx_reviews_search_id ON reviews(search_id)
COMMENT '基於search_id的查詢索引';

CREATE INDEX idx_reviews_review_id ON reviews(review_id)
COMMENT '基於review_id的查詢索引';

CREATE INDEX idx_reviews_iso_date ON reviews(iso_date)
COMMENT '基於發布日期的排序索引';

-- 針對 search_metadata 表的常用查詢欄位建立索引
CREATE INDEX idx_search_metadata_search_id ON search_metadata(search_id)
COMMENT '基於search_id的查詢索引';

-- =====================================================
-- 驗證表建立
-- =====================================================

-- 顯示所有表
SHOW TABLES;

-- 檢查 search_metadata 表結構
DESCRIBE search_metadata;

-- 檢查 reviews 表結構
DESCRIBE reviews;

-- 檢查索引建立情況
SHOW INDEX FROM search_metadata;
SHOW INDEX FROM reviews;

-- =====================================================
-- 表關聯說明
-- =====================================================
-- 業務關聯：reviews.search_id ↔ search_metadata.search_id
-- 一對多關係：一次搜尋對應多條評論
-- 查詢策略：通過 search_id 關聯兩表數據
-- 無約束原則：不使用外鍵約束，關聯完整性由應用程式負責
-- =====================================================

-- =====================================================
-- 資料處理流程參考
-- =====================================================
-- 1. 提取 search_metadata、place_info 存入 search_metadata 表
-- 2. 遍歷 reviews 陣列，每條評論存入 reviews 表
-- 3. 使用相同的 search_id 建立業務關聯
-- 4. 應用程式負責維護資料完整性
-- =====================================================