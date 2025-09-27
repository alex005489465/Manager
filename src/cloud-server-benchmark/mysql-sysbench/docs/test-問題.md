# MySQL + sysbench 系統故障排除指南

## 📝 文件說明

本文件記錄了MySQL + sysbench三層次性能測試系統在部署和運行過程中遇到的問題、解決方案和經驗總結。

**建立日期:** 2025-09-27  
**最後更新:** 2025-09-27  
**系統環境:** AWS c6g.xlarge (ARM Graviton2), Amazon Linux 2023

---

## 🚨 常見問題與解決方案

### 1. Docker 安裝問題

#### 問題：腳本文件沒有執行權限
```bash
sudo: ./docker_complete_installer.sh: command not found
```

**原因分析：**
- 腳本文件缺少執行權限（`-rw-rw-r--`）
- 新下載或創建的腳本默認沒有執行權限

**解決方案：**
```bash
# 檢查權限
ls -la docker_complete_installer.sh

# 添加執行權限
chmod +x docker_complete_installer.sh

# 然後執行
sudo ./docker_complete_installer.sh
```

**預防措施：**
- 下載腳本後先檢查權限
- 養成習慣性添加執行權限的做法

---

### 2. Docker 容器腳本權限問題

#### 問題：容器內腳本無法執行
```bash
bash: ./scripts/db-init.sh: Permission denied
```

**原因分析：**
- Docker volume 掛載的腳本文件沒有執行權限
- 容器內的腳本目錄是只讀掛載（`ro,noatime`）
- 需要在宿主機修改權限才能影響容器內的文件

**故障排查步驟：**

1. **檢查容器內權限：**
   ```bash
   docker exec -it sysbench-test ls -la /app/scripts/
   # 輸出：-rw-rw-r-- (缺少執行權限)
   ```

2. **嘗試容器內修改（會失敗）：**
   ```bash
   docker exec -it sysbench-test chmod +x /app/scripts/*.sh
   # 錯誤：Read-only file system
   ```

3. **檢查掛載狀態：**
   ```bash
   docker exec -it sysbench-test mount | grep scripts
   # 顯示：ro,noatime (只讀掛載)
   ```

**解決方案：**
```bash
# 在宿主機上修改權限
chmod +x /home/ec2-user/mysql-sysbench/scripts/*.sh

# 驗證修改成功
ls -la /home/ec2-user/mysql-sysbench/scripts/
# 應該顯示：-rwxrwxr-x

# 驗證容器內權限已更新
docker exec -it sysbench-test ls -la /app/scripts/
```

**關鍵學習點：**
- Docker volume 掛載時，文件權限由宿主機決定
- 只讀掛載的目錄無法在容器內修改權限
- 需要在宿主機修改權限，容器內會自動同步

---

### 3. MySQL 腳本 SQL 語法錯誤

#### 問題1：`current_user` 關鍵字衝突
```bash
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'current_user' at line 3
```

**原因分析：**
- `current_user` 是 MySQL 的保留關鍵字
- 在 MySQL 中用作列別名時可能產生語法衝突
- MySQL 5.6/8.0 對關鍵字的處理略有不同

**原始錯誤代碼：**
```sql
SELECT
    CONNECTION_ID() as connection_id,
    USER() as current_user,          -- 問題：current_user 是保留關鍵字
    DATABASE() as current_database,
    VERSION() as mysql_version,
    NOW() as current_time;
```

**解決方案：**
```sql
SELECT
    CONNECTION_ID() as connection_id,
    USER() as current_user_info,     -- 修改：避免使用保留關鍵字
    DATABASE() as current_database,
    VERSION() as mysql_version,
    NOW() as connection_time;
```

#### 問題2：`current_time` 關鍵字衝突
```bash
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'current_time' at line 6
```

**原因分析：**
- `current_time` 也是 MySQL 的保留關鍵字/函數名
- 作為列別名使用時產生衝突

**解決方案：**
```sql
-- 問題代碼
NOW() as current_time

-- 修正代碼  
NOW() as connection_time
```

#### 最終優化版本
為提高相容性和可讀性，最終簡化了 SQL 查詢：

```sql
SELECT 
    '$test_type 資料庫連接成功' AS status,
    DATABASE() AS db_name,
    USER() AS user_info,
    VERSION() AS mysql_ver;
```

**關鍵學習點：**
- 避免使用 MySQL 保留關鍵字作為列別名
- 簡化 SQL 查詢可提高相容性
- 在不同 MySQL 版本間測試 SQL 語句

---

## 🔧 調試技巧和工具

### 1. 權限問題調試

```bash
# 檢查文件權限
ls -la filename

# 檢查目錄權限
ls -ld directory/

# 檢查Docker掛載狀態
docker exec -it container mount | grep path

# 批量修改腳本權限
find /path -name "*.sh" -exec chmod +x {} \;
```

### 2. MySQL 連接問題調試

```bash
# 測試基本連接
mysql -h<host> -P<port> -u<user> -p<password> -e "SELECT 1;"

# 檢查用戶權限
mysql -h<host> -P<port> -u<user> -p<password> -e "SHOW GRANTS;"

# 測試資料庫存在性
mysql -h<host> -P<port> -u<user> -p<password> -e "SHOW DATABASES;"

# 簡單的 SQL 語法測試
mysql -h<host> -P<port> -u<user> -p<password> database -e "SELECT DATABASE();"
```

### 3. 容器狀態調試

```bash
# 查看容器狀態
docker ps -a

# 查看容器日誌
docker logs container-name

# 進入容器檢查
docker exec -it container-name bash

# 檢查容器資源使用
docker stats --no-stream
```

---

## 📋 檢查清單

### 部署前檢查
- [ ] Docker 已正確安裝並啟動
- [ ] 所有腳本文件都有執行權限（`chmod +x *.sh`）
- [ ] .env 文件配置正確（特別是 MySQL 主機 IP）
- [ ] 網絡連接正常（能 ping 通目標主機）

### 部署後檢查
- [ ] 所有容器都在運行（`docker ps`）
- [ ] MySQL 服務都能正常連接
- [ ] 資料庫和用戶已正確創建
- [ ] 腳本權限正確設置

### 測試前檢查
- [ ] 資料庫初始化完成
- [ ] 連接測試通過
- [ ] sysbench 工具可用

---

## 🎯 最佳實踐

### 1. 權限管理
```bash
# 統一設置腳本權限
find /project/scripts -name "*.sh" -exec chmod +x {} \;

# 檢查所有腳本權限
find /project -name "*.sh" -exec ls -la {} \;
```

### 2. SQL 語句編寫
```sql
-- 好的實踐：使用非保留關鍵字作為別名
SELECT 
    DATABASE() AS db_name,
    USER() AS user_info,
    VERSION() AS mysql_version;

-- 避免的寫法：使用保留關鍵字
SELECT 
    DATABASE() AS database,     -- 可能衝突
    USER() AS current_user,     -- 保留關鍵字
    VERSION() AS version;       -- 可能衝突
```

### 3. 錯誤處理
```bash
# 腳本中添加錯誤處理
set -e  # 遇到錯誤立即退出

# 函數中的錯誤處理
function_name() {
    if ! command; then
        log_error "操作失敗"
        return 1
    fi
    log_success "操作成功"
}
```

### 4. 日誌記錄
```bash
# 彩色日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}
```

---

## 🚀 成功部署確認

當看到以下輸出時，表示系統已成功部署：

```
============================================
[SUCCESS] 所有資料庫初始化完成！
============================================

資料庫連接資訊：
  CPU測試:    13.232.54.138:3306/cpu_test_db
  Memory測試: 13.232.54.138:3307/memory_test_db
  Disk測試:   13.232.54.138:3308/disk_test_db

使用者帳號： bench_user
密碼：       bench_pass_2025
```

---

## 📞 故障排除流程

1. **確認問題類型**
   - 權限問題？檢查文件權限
   - 連接問題？測試網絡和 MySQL 服務
   - SQL 錯誤？檢查語法和關鍵字

2. **收集信息**
   - 查看錯誤信息
   - 檢查日誌文件
   - 確認系統狀態

3. **逐步調試**
   - 從最簡單的操作開始
   - 逐步增加複雜度
   - 記錄每一步的結果

4. **驗證修復**
   - 重新執行失敗的操作
   - 確認問題已解決
   - 測試相關功能

---

## 📚 相關資源

- [MySQL 8.0 保留關鍵字列表](https://dev.mysql.com/doc/refman/8.0/en/keywords.html)
- [Docker Volume 文件](https://docs.docker.com/storage/volumes/)
- [Linux 文件權限管理](https://linux.die.net/man/1/chmod)
- [sysbench 官方文檔](https://github.com/akopytov/sysbench)

---

**維護者:** GitHub Copilot  
**聯絡方式:** 通過項目 README 或相關文檔  
**版本:** v1.0 (2025-09-27)