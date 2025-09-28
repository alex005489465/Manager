-- 初始化 benchdb 資料庫
CREATE DATABASE IF NOT EXISTS benchdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE benchdb;

-- 創建測試表
CREATE TABLE IF NOT EXISTS benchmark_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入測試數據 (10萬條)
DELIMITER $$

CREATE PROCEDURE InsertTestData()
BEGIN
    DECLARE i INT DEFAULT 1;

    WHILE i <= 100000 DO
        INSERT INTO benchmark_test (name, value) VALUES
        (CONCAT('test_', i), i * 10);
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

CALL InsertTestData();
DROP PROCEDURE InsertTestData;

-- 權限設定
GRANT ALL PRIVILEGES ON benchdb.* TO 'benchuser'@'%';
FLUSH PRIVILEGES;

-- 顯示創建的表
SHOW TABLES;

-- 顯示表的記錄數
SELECT 'benchmark_test' as table_name, COUNT(*) as record_count FROM benchmark_test;

-- 顯示數據樣本
SELECT * FROM benchmark_test ORDER BY id LIMIT 5;