# MySQL + sysbench 三層次性能測試系統

## 🎯 測試目標

本系統實現MySQL三層次性能測試，透過不同的記憶體配置模擬不同的性能瓶頸：
- **Layer 1 (CPU):** 純CPU運算能力測試
- **Layer 2 (Memory):** 記憶體頻寬與快取效率測試
- **Layer 3 (Disk):** 磁碟I/O吞吐量測試

## 📁 檔案結構

```
mysql-sysbench/
├── docker/
│   ├── bench-1/                        # MySQL容器配置 (部署在bench-1節點)
│   │   ├── docker-compose.yml          # 三個MySQL容器配置
│   │   └── mysql-config/
│   │       ├── mysql-cpu.cnf           # CPU測試專用配置 (6G buffer pool)
│   │       ├── mysql-memory.cnf        # 記憶體測試專用配置 (512M buffer pool)
│   │       └── mysql-disk.cnf          # 磁碟測試專用配置 (256M buffer pool)
│   └── test/                           # sysbench容器配置 (部署在test節點)
│       └── docker-compose.yml          # sysbench測試容器配置
├── scripts/
│   ├── db-init.sh                      # 資料庫初始化腳本
│   └── three-tier-test.sh              # 主要測試腳本
├── results/                            # 測試結果目錄
│   ├── cpu-test/                       # CPU測試結果
│   ├── memory-test/                    # 記憶體測試結果
│   └── disk-test/                      # 磁碟測試結果
└── README.md                           # 本文件
```

## 🚀 部署步驟

### 1. 在 bench-1 節點部署MySQL容器

```bash
# 進入bench-1目錄
cd mysql-sysbench/docker/bench-1

# 啟動三個MySQL容器
docker-compose up -d

# 查看容器狀態
docker-compose ps
```

### 2. 在 test 節點部署sysbench測試容器

```bash
# 進入test目錄
cd mysql-sysbench/docker/test

# 編輯.env檔案，設定bench-1節點的公網IP
# 修改以下變數：
# MYSQL_HOST_CPU=<bench-1-public-ip>
# MYSQL_HOST_MEMORY=<bench-1-public-ip>
# MYSQL_HOST_DISK=<bench-1-public-ip>

# 啟動sysbench測試容器
docker-compose up -d

# 查看容器狀態
docker-compose ps
```

### 3. 初始化資料庫

```bash
# 進入sysbench容器
docker exec -it sysbench-test bash

# 執行資料庫初始化
./scripts/db-init.sh
```

### 4. 執行三層次測試

```bash
# 在sysbench容器內執行完整測試
./scripts/three-tier-test.sh
```

## ⚙️ 測試配置

### MySQL容器配置

| 容器類型 | 埠號 | Buffer Pool | Log檔案 | 測試目標 |
|----------|------|-------------|---------|----------|
| MySQL-CPU | 3306 | 6G | 512M | CPU性能測試 |
| MySQL-Memory | 3307 | 512M | 256M | 記憶體壓力測試 |
| MySQL-Disk | 3308 | 256M | 128M | 磁碟I/O測試 |

### 測試資料量

| 測試層次 | 資料量 | 估計大小 | Buffer Pool命中率 |
|----------|--------|----------|------------------|
| Layer 1 (CPU) | 10萬筆記錄 | ~20MB | ~100% |
| Layer 2 (Memory) | 500萬筆記錄 | ~1GB | 50-70% |
| Layer 3 (Disk) | 5000萬筆記錄 | ~10GB | 10-20% |

### 測試參數

- **執行緒數:** 1, 4, 16
- **測試時間:** 每個執行緒數測試3分鐘 (180秒)
- **測試類型:** oltp_read_only (純讀取測試)

## 🔧 環境變數配置

### bench-1 節點 (.env 檔案)

編輯 `mysql-sysbench/docker/bench-1/.env` 檔案：

```bash
# MySQL 映像檔配置
MYSQL_IMAGE=mysql:5.6

# MySQL 認證設定
MYSQL_ROOT_PASSWORD=mysql_bench_2025
MYSQL_USER=bench_user
MYSQL_PASSWORD=bench_pass_2025

# MySQL 資料庫名稱
MYSQL_CPU_DATABASE=cpu_test_db
MYSQL_MEMORY_DATABASE=memory_test_db
MYSQL_DISK_DATABASE=disk_test_db

# MySQL 埠號設定
MYSQL_CPU_PORT=3306
MYSQL_MEMORY_PORT=3307
MYSQL_DISK_PORT=3308
```

### test 節點 (.env 檔案)

編輯 `mysql-sysbench/docker/test/.env` 檔案，**重要：需要修改MySQL主機IP**：

```bash
# MySQL 連接設定 (必須修改為 bench-1 節點的公網 IP)
MYSQL_HOST_CPU=<bench-1-public-ip>
MYSQL_HOST_MEMORY=<bench-1-public-ip>
MYSQL_HOST_DISK=<bench-1-public-ip>

# MySQL 埠號設定
MYSQL_PORT_CPU=3306
MYSQL_PORT_MEMORY=3307
MYSQL_PORT_DISK=3308

# MySQL 認證設定 (需與 bench-1 節點設定一致)
MYSQL_USER=bench_user
MYSQL_PASSWORD=bench_pass_2025

# 測試參數配置
TEST_THREADS=1,4,16
TEST_DURATION=180
```

## 📊 結果輸出

### 測試結果檔案

測試完成後，結果將儲存在 `results/` 目錄下：

```
results/
├── cpu-test/
│   ├── CPU_1threads_20250927_143022.txt
│   ├── CPU_4threads_20250927_143545.txt
│   └── CPU_16threads_20250927_144108.txt
├── memory-test/
│   ├── Memory_1threads_20250927_144631.txt
│   ├── Memory_4threads_20250927_145154.txt
│   └── Memory_16threads_20250927_145717.txt
├── disk-test/
│   ├── Disk_1threads_20250927_150240.txt
│   ├── Disk_4threads_20250927_150803.txt
│   └── Disk_16threads_20250927_151326.txt
└── test_summary_20250927_143022.txt
```

### 關鍵性能指標

每個測試結果檔案包含：
- **TPS** (每秒事務數)
- **QPS** (每秒查詢數)
- **平均響應時間**
- **95%、99%百分位響應時間**
- **最小/最大響應時間**

## 🛠️ 故障排除

### 常見問題

1. **MySQL容器啟動失敗**
   ```bash
   # 檢查記憶體使用量
   docker stats

   # 檢查容器日誌
   docker-compose logs mysql-cpu
   ```

2. **test節點無法連接bench-1**
   ```bash
   # 檢查網路連通性
   telnet <bench-1-ip> 3306

   # 檢查安全群組設定
   # 確保bench-1開放3306, 3307, 3308埠給test節點
   ```

3. **sysbench測試失敗**
   ```bash
   # 手動測試資料庫連接
   mysql -h<bench-1-ip> -P3306 -ubench_user -pbench_pass_2025 cpu_test_db

   # 檢查sysbench版本
   sysbench --version
   ```

### 記憶體不足處理

如果遇到記憶體不足，可以調整配置：

```bash
# 編輯MySQL配置檔案，減少buffer pool大小
# mysql-cpu.cnf: innodb_buffer_pool_size = 4G
# mysql-memory.cnf: innodb_buffer_pool_size = 256M
# mysql-disk.cnf: innodb_buffer_pool_size = 128M
```

## ⏱️ 預估執行時間

- **資料準備:**
  - CPU測試: ~30秒
  - Memory測試: ~5分鐘
  - Disk測試: ~15分鐘

- **測試執行:**
  - 每層次3個執行緒 × 3分鐘 = 9分鐘
  - 總計: ~27分鐘

- **總時間:** 約1.5-2小時 (包含資料準備)

## 💰 成本估算

- **3台c6g.xlarge實例:** 0.2556 USD/hour
- **測試時間:** 2小時
- **預估成本:** ~0.51 USD

## 📝 注意事項

### ARM架構考量
- 使用ARM64相容的Docker映像檔
- MySQL 5.6官方支援ARM架構
- sysbench工具已驗證ARM相容性

### 安全設定
- **預設密碼:** `mysql_bench_2025` (生產環境請修改)
- **測試帳號:** bench_user / bench_pass_2025
- **網路:** 確保正確設定EC2安全群組

### 資源監控
- 建議在測試期間監控系統資源使用率
- 磁碟空間至少預留15GB
- 記憶體使用約7GB (預留1GB給系統)

---

**建立日期:** 2025-09-27
**版本:** v1.0
**適用環境:** AWS c6g.xlarge (ARM Graviton2)