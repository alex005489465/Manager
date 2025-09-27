# MySQL sysbench 測試腳本改進記錄

## 📝 文件說明

本文件記錄了對 `three-tier-test.sh` 腳本的功能改進，包括表大小檢查功能的新增和測試資料量的調整。

**建立日期:** 2025-09-27  
**腳本版本:** v2.0  
**修改者:** GitHub Copilot  
**系統環境:** AWS c6g.xlarge (ARM Graviton2), Amazon Linux 2023

---

## 🎯 改進目標

1. **增加表大小可見性**：在測試前後顯示實際資料表大小
2. **優化測試資料量**：減少磁碟測試的資料量以提高效率
3. **完整測試記錄**：在測試結果文件中包含資料表資訊

---

## 🔧 主要修改內容

### 1. 測試資料量調整

#### 修改前：
```bash
DISK_TABLE_SIZE=50000000   # 5000萬筆記錄 (~10GB)
```

#### 修改後：
```bash
DISK_TABLE_SIZE=10000000   # 1000萬筆記錄 (~2GB)
```

**改進理由：**
- **效率考量**：5000萬條記錄需要約15分鐘準備時間，1000萬條只需約3分鐘
- **資源節約**：減少磁碟空間使用，從10GB降至2GB
- **測試有效性**：1000萬條記錄仍足以測試磁碟I/O性能

### 2. 新增表大小檢查功能

#### 新增函數：`check_table_size()`

```bash
check_table_size() {
    local host=$1
    local port=$2
    local database=$3
    local test_type=$4

    log_info "檢查 $test_type 測試表大小..."

    local size_info=$(mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS SIZE_MB,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 2) AS SIZE_GB
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = '$database' AND TABLE_NAME = 'sbtest1';
    " 2>/dev/null)

    if [ -n "$size_info" ] && [[ "$size_info" != *"Empty set"* ]]; then
        echo "$size_info" | while read -r line; do
            if [[ "$line" != *"TABLE_NAME"* ]]; then
                log_success "$test_type 測試表資訊: $line"
            fi
        done
    else
        log_warning "$test_type 測試表不存在或為空"
    fi
}
```

**功能特點：**
- 顯示表名、記錄數、MB和GB大小
- 彩色輸出，增強可讀性
- 錯誤處理機制

### 3. 新增測試結果文件記錄功能

#### 新增函數：`get_table_size_info()`

```bash
get_table_size_info() {
    local host=$1
    local port=$2
    local database=$3

    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        SELECT 
            CONCAT('表名: ', TABLE_NAME),
            CONCAT('記錄數: ', FORMAT(TABLE_ROWS, 0)),
            CONCAT('資料大小: ', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2), ' MB (', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 3), ' GB)')
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = '$database' AND TABLE_NAME = 'sbtest1';
    " 2>/dev/null | tail -n +2 | tr '\t' '\n'
}
```

**功能特點：**
- 返回格式化的表大小資訊
- 使用千位分隔符顯示記錄數
- 同時提供MB和GB單位

### 4. 修改測試執行流程

#### 修改 `prepare_test_data()` 函數

```bash
# 修改前：只有成功訊息
if [ $? -eq 0 ]; then
    log_success "$test_type 測試資料準備完成"
else
    log_error "$test_type 測試資料準備失敗"
    return 1
fi

# 修改後：添加表大小檢查
if [ $? -eq 0 ]; then
    log_success "$test_type 測試資料準備完成"
    
    # 檢查插入的資料表大小
    check_table_size "$host" "$port" "$database" "$test_type"
else
    log_error "$test_type 測試資料準備失敗"
    return 1
fi
```

#### 修改 `run_single_test()` 函數

```bash
# 修改前：基本測試資訊
{
    echo "=== MySQL $test_type 性能測試結果 ==="
    echo "測試時間: $(date)"
    echo "測試類型: $test_type"
    echo "執行緒數: $threads"
    echo "測試時長: $TEST_DURATION 秒"
    echo "目標主機: ${host}:${port}"
    echo "測試資料庫: $database"
    echo "=================================="
    echo

    sysbench oltp_read_only [...]
} | tee "$result_file"

# 修改後：添加表大小資訊
{
    echo "=== MySQL $test_type 性能測試結果 ==="
    echo "測試時間: $(date)"
    echo "測試類型: $test_type"
    echo "執行緒數: $threads"
    echo "測試時長: $TEST_DURATION 秒"
    echo "目標主機: ${host}:${port}"
    echo "測試資料庫: $database"
    echo "=================================="
    echo
    echo "測試資料表資訊:"
    get_table_size_info "$host" "$port" "$database"
    echo "=================================="
    echo

    sysbench oltp_read_only [...]
} | tee "$result_file"
```

---

## 📊 改進效果

### 1. 終端輸出改進

**修改前：**
```
[SUCCESS] CPU 測試資料準備完成
```

**修改後：**
```
[SUCCESS] CPU 測試資料準備完成
[INFO] 檢查 CPU 測試表大小...
[SUCCESS] CPU 測試表資訊: sbtest1    100000    20.50    0.02
```

### 2. 測試結果文件改進

**修改前：**
```
=== MySQL CPU 性能測試結果 ===
測試時間: 2025-09-27 17:30:00
測試類型: CPU
執行緒數: 4
測試時長: 180 秒
目標主機: 13.232.54.138:3306
測試資料庫: cpu_test_db
==================================

sysbench 1.0.20 (using system LuaJIT 2.1.0-beta3)
[測試結果...]
```

**修改後：**
```
=== MySQL CPU 性能測試結果 ===
測試時間: 2025-09-27 17:30:00
測試類型: CPU
執行緒數: 4
測試時長: 180 秒
目標主機: 13.232.54.138:3306
測試資料庫: cpu_test_db
==================================

測試資料表資訊:
表名: sbtest1
記錄數: 100,000
資料大小: 20.50 MB (0.020 GB)
==================================

sysbench 1.0.20 (using system LuaJIT 2.1.0-beta3)
[測試結果...]
```

### 3. 測試效率改進

| 測試類型 | 修改前資料量 | 修改後資料量 | 預估準備時間 | 磁碟使用 |
|----------|-------------|-------------|-------------|----------|
| CPU      | 10萬條      | 10萬條      | ~30秒       | ~20MB    |
| Memory   | 500萬條     | 500萬條     | ~5分鐘      | ~1GB     |
| Disk     | 5000萬條    | **1000萬條** | **~3分鐘** (↓12分鐘) | **~2GB** (↓8GB) |

**總改進：**
- **準備時間縮短**：約20分鐘 → 8.5分鐘 (節省58%)
- **磁碟空間節省**：約11GB → 3GB (節省73%)
- **保持測試有效性**：1000萬條記錄仍足以測試磁碟I/O性能

---

## 🎯 功能驗證

### 1. 表大小檢查功能測試

```bash
# 測試命令
docker exec -it sysbench-test mysql -h13.232.54.138 -P3306 -ubench_user -pbench_pass_2025 cpu_test_db -e "
SELECT 
    CONCAT('表名: ', TABLE_NAME),
    CONCAT('記錄數: ', FORMAT(TABLE_ROWS, 0)),
    CONCAT('資料大小: ', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2), ' MB (', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 3), ' GB)')
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'cpu_test_db' AND TABLE_NAME = 'sbtest1';
" 2>/dev/null | tail -n +2 | tr '\t' '\n'

# 預期輸出
表名: sbtest1
記錄數: 1,000
資料大小: 0.27 MB (0.000 GB)
```

### 2. 腳本權限確認

```bash
# 檢查權限
ls -la /home/ec2-user/mysql-sysbench/scripts/three-tier-test.sh
# 應該顯示：-rwxrwxr-x
```

---

## 🔍 技術細節

### 1. SQL查詢優化

**表大小查詢：**
```sql
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS SIZE_MB,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 2) AS SIZE_GB
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'database_name' AND TABLE_NAME = 'sbtest1';
```

**關鍵點：**
- `DATA_LENGTH + INDEX_LENGTH`：獲取完整表大小（數據+索引）
- `ROUND(..., 2)`：保留兩位小數
- `FORMAT(TABLE_ROWS, 0)`：千位分隔符顯示記錄數

### 2. Bash 處理技巧

**格式化輸出：**
```bash
# 將MySQL的tab分隔輸出轉換為換行分隔
mysql [...] | tail -n +2 | tr '\t' '\n'

# tail -n +2: 跳過表頭
# tr '\t' '\n': 將tab轉換為換行
```

### 3. 錯誤處理

```bash
# 靜默錯誤輸出但保持功能
mysql [...] 2>/dev/null

# 檢查輸出是否有效
if [ -n "$size_info" ] && [[ "$size_info" != *"Empty set"* ]]; then
    # 處理有效輸出
else
    log_warning "測試表不存在或為空"
fi
```

---

## 📋 使用指南

### 1. 執行腳本

```bash
# 進入sysbench容器
docker exec -it sysbench-test bash

# 執行測試（需要MySQL重建完成）
./app/scripts/three-tier-test.sh
```

### 2. 查看結果

```bash
# 查看結果目錄
ls -la /app/results/

# 查看特定測試結果
cat /app/results/cpu-test/CPU_1threads_20250927_172937.txt
```

### 3. 預期輸出

**終端輸出會包含：**
- 測試進度資訊
- 表大小檢查結果
- 實時性能數據

**結果文件會包含：**
- 完整的測試配置資訊
- 資料表大小資訊
- 詳細的性能測試結果

---

## 🚀 未來改進建議

### 1. 功能增強
- **歷史比較**：添加與歷史測試結果的對比功能
- **圖表生成**：自動生成性能趨勢圖
- **報告格式**：支援生成PDF或HTML格式報告

### 2. 監控增強
- **資源監控**：測試期間記錄CPU、記憶體使用率
- **網絡監控**：記錄網絡延遲和吞吐量
- **系統狀態**：記錄系統負載和磁碟I/O狀態

### 3. 自動化改進
- **郵件通知**：測試完成後自動發送結果
- **定時執行**：支援cron定時執行測試
- **結果上傳**：自動上傳結果到雲端儲存

---

## 📞 疑難解答

### 1. 表大小顯示為空

**可能原因：**
- 測試表不存在
- 資料庫連接失敗
- 權限不足

**解決方法：**
```bash
# 檢查表是否存在
mysql -h<host> -P<port> -u<user> -p<password> <database> -e "SHOW TABLES;"

# 檢查表狀態
mysql -h<host> -P<port> -u<user> -p<password> <database> -e "SHOW TABLE STATUS LIKE 'sbtest1';"
```

### 2. 權限錯誤

**解決方法：**
```bash
# 在宿主機修改權限
chmod +x /home/ec2-user/mysql-sysbench/scripts/*.sh
```

### 3. SQL語法錯誤

**檢查方法：**
```bash
# 手動測試SQL查詢
mysql -h<host> -P<port> -u<user> -p<password> <database> -e "<SQL_QUERY>"
```

---

## 📚 參考資源

- [MySQL information_schema.TABLES 文檔](https://dev.mysql.com/doc/refman/8.0/en/information-schema-tables-table.html)
- [sysbench 官方文檔](https://github.com/akopytov/sysbench)
- [Bash 腳本最佳實踐](https://google.github.io/styleguide/shellguide.html)

---

**文件版本:** v1.0  
**最後更新:** 2025-09-27  
**維護者:** GitHub Copilot