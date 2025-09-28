-- 初始化 benchdb 資料庫
CREATE DATABASE IF NOT EXISTS benchdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE benchdb;

-- 創建測試表
CREATE TABLE IF NOT EXISTS benchmark_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_timestamp (timestamp)
);

-- 插入測試數據
INSERT INTO benchmark_test (name, value) VALUES
('test_1', 100),
('test_2', 200),
('test_3', 300),
('test_4', 400),
('test_5', 500),
('test_6', 600),
('test_7', 700),
('test_8', 800),
('test_9', 900),
('test_10', 1000);

-- 創建一個用於性能測試的大表
CREATE TABLE IF NOT EXISTS performance_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    data_value DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
);

-- 填充性能測試數據
INSERT INTO performance_data (category, data_value, description)
SELECT
    CONCAT('category_', (id % 10) + 1) AS category,
    ROUND(RAND() * 1000, 2) AS data_value,
    CONCAT('Test data entry number ', id) AS description
FROM benchmark_test
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) t1
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) t2;

-- 權限設定
GRANT ALL PRIVILEGES ON benchdb.* TO 'benchuser'@'%';
FLUSH PRIVILEGES;

-- 顯示創建的表
SHOW TABLES;

-- 顯示表的記錄數
SELECT 'benchmark_test' as table_name, COUNT(*) as record_count FROM benchmark_test
UNION ALL
SELECT 'performance_data' as table_name, COUNT(*) as record_count FROM performance_data;