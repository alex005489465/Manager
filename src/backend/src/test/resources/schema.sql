-- Manager 系統測試環境資料表結構
-- 此檔案將在測試開始時自動執行，建立必要的資料表結構

-- 注意：實際的資料表結構應該根據設計文件定義
-- 這裡僅為範例，展示測試環境的資料表建立方式（MySQL語法）

-- 範例資料表 (待 Manager 系統設計文件更新)
/*
CREATE TABLE IF NOT EXISTS example_table (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
*/