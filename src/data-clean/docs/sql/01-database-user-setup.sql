-- =====================================================
-- Manager專案 - 資料庫和使用者設定腳本
-- 適用於 MySQL 9.4.0
-- 執行環境：phpMyAdmin (使用 root 帳號執行)
-- =====================================================

-- 建立專案資料庫
-- 使用 utf8mb4 字符集以支援完整 Unicode (包含 emoji)
CREATE DATABASE IF NOT EXISTS manager_reviews_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 建立專案專用使用者
-- 允許從任何主機連接 (%)，適用於 Docker 環境
CREATE USER IF NOT EXISTS 'manager_reviews_user'@'%' IDENTIFIED BY 'MgrRev2024!@#';

-- 授予專案使用者對指定資料庫的完整操作權限
-- 遵循最小權限原則，僅授予必要權限
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
ON manager_reviews_db.*
TO 'manager_reviews_user'@'%';

-- 刷新權限表，使設定立即生效
FLUSH PRIVILEGES;

-- =====================================================
-- 驗證設定
-- =====================================================

-- 驗證資料庫建立成功
SHOW DATABASES LIKE 'manager_reviews_db';

-- 驗證使用者建立成功
SELECT User, Host FROM mysql.user WHERE User = 'manager_reviews_user';

-- 驗證使用者權限
SHOW GRANTS FOR 'manager_reviews_user'@'%';

-- =====================================================
-- 配置資訊摘要
-- =====================================================
-- 資料庫名稱: manager_reviews_db
-- 使用者帳號: manager_reviews_user
-- 使用者密碼: MgrRev2024!@#
-- 字符集: utf8mb4_unicode_ci
-- 權限範圍: 僅限 manager_reviews_db 資料庫
-- =====================================================