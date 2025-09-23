# MeowManager 資料庫基礎設施

這個目錄包含了 MeowManager 專案的 MySQL 資料庫和管理工具的 Docker 配置。

## 服務組成

- **MySQL 9.4.0**: 主資料庫服務 (最新 Innovation Release)
- **phpMyAdmin**: 傳統的網頁資料庫管理介面
- **Adminer**: 輕量級的資料庫管理工具

## 快速開始

### 1. 環境設定

```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定您的資料庫密碼
```

### 2. 啟動服務

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 3. 存取管理介面

- **phpMyAdmin**: http://localhost:8080
- **Adminer**: http://localhost:8081
- **MySQL 直連**: localhost:3306

## MySQL 9.4.0 重要變化

- **認證機制**: 預設使用 `caching_sha2_password`，提供更強的安全性
- **移除功能**: 不再支援 `mysql_native_password` 認證插件
- **效能提升**: Innovation Release 包含最新的效能改進和錯誤修復
- **相容性**: phpMyAdmin 和 Adminer 皆已支援新的認證機制

## 管理工具比較

| 特性 | phpMyAdmin | Adminer |
|------|------------|---------|
| 檔案大小 | 13.7 MB | 478 KB |
| 效能 | 一般 | 快 28% |
| 支援資料庫 | MySQL/MariaDB | MySQL, PostgreSQL, SQLite, MongoDB 等 |
| 功能完整性 | 非常完整 | 核心功能齊全 |
| 適用場景 | 複雜管理任務 | 快速操作和輕量需求 |

## 目錄結構

```
infra/
├── docker-compose.yml      # Docker Compose 配置
├── .env.example           # 環境變數範例
├── .env                   # 實際環境變數 (需自行創建)
├── mysql/
│   ├── init/             # 資料庫初始化 SQL 腳本
│   └── conf/             # MySQL 配置檔案
└── README.md             # 本說明文件
```

## 常用指令

```bash
# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 僅重啟特定服務
docker-compose restart mysql

# 查看 MySQL 日誌
docker-compose logs mysql

# 進入 MySQL 容器
docker-compose exec mysql mysql -u root -p

# 備份資料庫
docker-compose exec mysql mysqldump -u root -p meow_manager > backup.sql

# 還原資料庫
docker-compose exec -T mysql mysql -u root -p meow_manager < backup.sql
```

## 資料持久化

- MySQL 資料儲存在 Docker Volume `mysql_data` 中
- 即使刪除容器，資料也會保留
- 若需完全清除資料：`docker volume rm infra_mysql_data`

## 初始化腳本

將 SQL 腳本放在 `mysql/init/` 目錄中，會在資料庫首次啟動時自動執行。
腳本執行順序按檔名字母順序。

## 自訂配置

MySQL 的自訂配置檔案可放在 `mysql/conf/` 目錄中，格式為 `.cnf`。

## 安全注意事項

1. 修改 `.env` 中的預設密碼
2. 生產環境請關閉管理介面的外部存取
3. 定期備份資料庫
4. 監控容器日誌

## 疑難排解

### 常見問題

1. **端口衝突**: 修改 `.env` 中的端口設定
2. **權限問題**: 確保 Docker 有足夠權限
3. **記憶體不足**: 調整 Docker 記憶體配置

### 重置資料庫

```bash
# 停止服務並刪除資料
docker-compose down -v

# 重新啟動
docker-compose up -d
```