# MySQL Docker 容器問題診斷與解決記錄

**日期**: 2025年9月27日  
**環境**: Amazon Linux 2023, Docker 25.0.8, Docker Compose v2.39.4  
**項目**: MySQL Sysbench 基準測試環境  

## 問題概述

在部署 MySQL Sysbench 測試環境時，遇到了多個 Docker 容器持續重啟的問題。經過系統性診斷和修復，最終成功部署了三個不同配置的 MySQL 容器用於 CPU、記憶體和磁盤性能測試。

## 問題清單與解決方案

### 1. 🔴 記憶體配置過高問題

**問題描述**:
- CPU 測試容器配置了 6GB 的 InnoDB buffer pool
- 系統總記憶體只有 7.6GB，導致記憶體不足
- 容器在初始化階段就重啟

**診斷方法**:
```bash
# 檢查系統記憶體
free -h

# 檢查容器狀態
docker ps
docker logs mysql-cpu-test --tail 20
```

**解決方案**:
- 將 CPU 容器的 buffer pool 從 6GB 調整為 1GB
- 記憶體容器保持 512MB（合理範圍）
- 磁盤容器保持 256MB（符合測試目標）

**修改文件**: `mysql-config/mysql-cpu.cnf`
```ini
# 修改前
innodb_buffer_pool_size = 6G

# 修改後  
innodb_buffer_pool_size = 1G
```

### 2. 🔴 MySQL 8.0 過時參數問題

**問題描述**:
- 配置文件使用了 MySQL 8.0 已移除的 `query_cache_type` 和 `query_cache_size` 參數
- 導致 MySQL 服務無法啟動，出現 "unknown variable" 錯誤

**診斷方法**:
```bash
# 查看容器錯誤日誌
docker logs mysql-cpu-test --tail 50 | grep -i "error\|unknown"
```

**錯誤信息**:
```
[ERROR] [MY-000067] [Server] unknown variable 'query_cache_type=0'
```

**解決方案**:
- 移除所有三個配置文件中的 query cache 相關配置
- MySQL 8.0 已默認移除查詢緩存功能

**修改文件**: 所有 `mysql-config/*.cnf` 文件
```ini
# 移除這些行
query_cache_type = 0
query_cache_size = 0

# 替換為註釋
# MySQL 8.0 已移除 query cache，不需要這些配置
```

### 3. 🔴 日誌路徑權限問題

**問題描述**:
- 配置文件指定了 `/var/log/mysql/` 路徑用於錯誤日誌和慢查詢日誌
- 容器中該目錄不存在或權限不足

**診斷方法**:
```bash
# 檢查配置文件中的日誌路徑
grep -n "log-error\|slow_query_log_file" mysql-config/*
```

**解決方案**:
- 註釋掉自定義日誌路徑配置
- 讓 MySQL 使用默認日誌路徑

**修改示例**:
```ini
# 修改前
log-error = /var/log/mysql/error.log
slow_query_log_file = /var/log/mysql/slow.log

# 修改後
# log-error = /var/log/mysql/error.log  # 使用默認路徑
# slow_query_log_file = /var/log/mysql/slow.log  # 使用默認路徑
```

### 4. 🔴 數據卷損壞問題

**問題描述**:
- 在測試過程中，容器多次異常重啟導致數據卷中的 MySQL 系統表損壞
- 出現 "Table 'mysql.user' doesn't exist" 等錯誤

**診斷方法**:
```bash
# 檢查容器日誌中的數據庫錯誤
docker logs mysql-memory-test --tail 15
```

**錯誤信息**:
```
[ERROR] [MY-010326] [Server] Fatal error: Can't open and lock privilege tables: Table 'mysql.user' doesn't exist
```

**解決方案**:
```bash
# 停止容器並刪除損壞的數據卷
docker-compose stop mysql-memory
docker rm mysql-memory-test
docker volume rm bench-1_mysql_memory_data

# 重新創建容器，讓 MySQL 重新初始化
docker-compose up -d mysql-memory
```

### 5. 🔴 Socket 路徑問題

**問題描述**:
- 使用默認 socket 路徑 `/var/run/mysqld/mysqld.sock` 連接失敗
- 配置文件中指定了 `/tmp/mysql.sock`

**診斷方法**:
```bash
# 檢查 MySQL 啟動日誌中的 socket 路徑
docker logs mysql-cpu-test | grep "ready for connections"
```

**解決方案**:
```bash
# 使用正確的 socket 路徑連接
docker exec mysql-cpu-test mysql -S /tmp/mysql.sock -u root -p...
```

## 診斷思路與方法

### 系統性診斷流程

1. **容器狀態檢查**
   ```bash
   docker ps              # 查看運行狀態
   docker-compose ps      # 查看服務狀態
   ```

2. **日誌分析**
   ```bash
   docker logs <container> --tail 50    # 查看最近日誌
   docker logs <container> | grep -i error  # 過濾錯誤信息
   ```

3. **資源檢查**
   ```bash
   free -h               # 檢查記憶體使用
   df -h                 # 檢查磁盤空間
   ```

4. **配置驗證**
   ```bash
   # 使用簡化配置測試
   # 逐步添加配置項定位問題
   ```

### 問題隔離策略

1. **最小可行配置**: 先用最簡單的配置確保容器能啟動
2. **逐步增加複雜性**: 一次添加一個配置項，定位具體問題
3. **分別測試**: 單獨測試每個容器，避免多個問題混淆

## 最終配置總結

### 系統資源分配
- 總記憶體: 7.6GB
- CPU 容器: 1GB buffer pool (適合 CPU 密集測試)
- 記憶體容器: 512MB buffer pool (中等記憶體壓力)
- 磁盤容器: 256MB buffer pool (強制磁盤 I/O)

### 容器端口映射
- mysql-cpu-test: 3306 → 3306
- mysql-memory-test: 3307 → 3306  
- mysql-disk-test: 3308 → 3306

### 配置優化要點
- 移除 MySQL 8.0 不支持的參數
- 使用默認日誌路徑避免權限問題
- 根據系統資源合理配置記憶體
- 保留必要的性能調優參數

## 測試驗證

最終驗證所有容器正常運行：

```bash
# 測試連接
docker exec mysql-cpu-test mysql -S /tmp/mysql.sock -u root -pmysql_bench_2025 -e "SELECT 'CPU MySQL container - Running Successfully' as status;"

docker exec mysql-memory-test mysql -S /tmp/mysql.sock -u root -pmysql_bench_2025 -e "SELECT 'Memory MySQL container - Running Successfully' as status;"

docker exec mysql-disk-test mysql -S /tmp/mysql.sock -u root -pmysql_bench_2025 -e "SELECT 'Disk MySQL container - Running Successfully' as status;"
```

## 經驗教訓

1. **配置文件版本兼容性**: 不同 MySQL 版本的配置參數會有變化，需要檢查兼容性
2. **資源評估的重要性**: 在容器化環境中，需要準確評估系統資源
3. **逐步調試法**: 複雜問題應該分解為小問題逐一解決
4. **日誌分析技巧**: 善用日誌過濾和搜索來快速定位問題
5. **數據持久化注意事項**: 開發測試階段要注意數據卷的清理和重建

## 參考文檔

- [MySQL 8.0 配置參數文檔](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html)
- [Docker Compose 服務配置](https://docs.docker.com/compose/compose-file/)
- [InnoDB 存儲引擎配置](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html)

---
**維護者**: GitHub Copilot  
**最後更新**: 2025年9月27日  
**狀態**: 已解決，環境正常運行