# MySQL + sysbench 測試系統實現計劃

## 🎯 實現目標
建立完整的MySQL三層次性能測試系統，包含Docker容器配置、自動化測試腳本和結果儲存功能。

## 📋 實現步驟

### 第一階段：目錄結構建立 (5分鐘)
1. 建立 `mysql-sysbench/` 主目錄
2. 建立子目錄：`docker/`, `scripts/`, `results/`
3. 建立特定配置目錄：`docker/bench-1/`, `docker/test/`, `docker/bench-1/mysql-config/`

### 第二階段：Docker配置檔案 (20分鐘)
1. **bench-1/docker-compose.yml** - 三個MySQL 5.6容器配置
   - MySQL-CPU容器 (port 3306, 6G buffer pool)
   - MySQL-Memory容器 (port 3307, 512M buffer pool)
   - MySQL-Disk容器 (port 3308, 256M buffer pool)
2. **mysql-config/** - 三個不同的my.cnf配置檔案
   - 針對CPU/Memory/Disk測試的差異化配置
3. **test/docker-compose.yml** - sysbench測試容器配置
   - ARM64相容的sysbench映像檔
   - 掛載測試腳本和結果目錄

### 第三階段：測試腳本開發 (25分鐘)
1. **three-tier-test.sh** - 主要測試腳本
   - 三層次測試自動化執行
   - 測試資料準備 (10萬/500萬/5000萬筆記錄)
   - 多執行緒測試 (1, 4, 16 threads)
   - 結果儲存功能
2. **資料庫初始化腳本**
   - 自動建立測試資料庫
   - 權限設定腳本

## 🔧 技術要點

### ARM架構支援
- 使用官方MySQL 5.6 ARM映像檔
- 採用ARM相容的sysbench工具
- 確保所有依賴套件支援ARM64

### 網路配置
- 配置容器間網路連接
- 設定正確的埠對應
- 支援跨EC2實例連接

### 資源優化
- 記憶體配置符合8GB實例限制
- 磁碟空間管理 (預留15GB+)
- CPU資源合理分配

## 📊 詳細實現清單

### 需要建立的檔案

```
mysql-sysbench/
├── docker/
│   ├── bench-1/
│   │   ├── docker-compose.yml              # 三個MySQL容器配置
│   │   └── mysql-config/
│   │       ├── mysql-cpu.cnf               # CPU測試專用配置
│   │       ├── mysql-memory.cnf            # 記憶體測試專用配置
│   │       └── mysql-disk.cnf              # 磁碟測試專用配置
│   └── test/
│       └── docker-compose.yml              # sysbench容器配置
├── scripts/
│   ├── three-tier-test.sh                  # 主要測試腳本
│   └── db-init.sh                          # 資料庫初始化腳本
├── results/
│   ├── cpu-test/                           # CPU測試結果
│   ├── memory-test/                        # 記憶體測試結果
│   └── disk-test/                          # 磁碟測試結果
└── README.md                               # 使用說明文件
```

### Docker容器配置重點

#### MySQL容器配置差異
| 容器類型 | 埠號 | Buffer Pool | Log檔案大小 | 用途 |
|----------|------|-------------|-------------|------|
| MySQL-CPU | 3306 | 6G | 512M | CPU性能測試 |
| MySQL-Memory | 3307 | 512M | 256M | 記憶體壓力測試 |
| MySQL-Disk | 3308 | 256M | 128M | 磁碟I/O測試 |

#### sysbench容器要求
- 支援ARM64架構
- 預安裝mysql-client
- 掛載腳本和結果目錄
- 網路可達MySQL容器

### 測試腳本功能規劃

#### 主測試腳本 (three-tier-test.sh)
1. **環境檢查**
   - Docker容器狀態確認
   - 網路連通性測試
   - 資料庫連接測試

2. **測試執行流程**
   - Layer 1 (CPU): 10萬筆記錄，1/4/16執行緒，各3分鐘
   - Layer 2 (Memory): 500萬筆記錄，1/4/16執行緒，各3分鐘
   - Layer 3 (Disk): 5000萬筆記錄，1/4/16執行緒，各3分鐘

3. **結果儲存**
   - 自動儲存測試日誌
   - 原始sysbench輸出保存
   - 生成時間戳記

#### 資料庫初始化腳本 (db-init.sh)
- 建立測試資料庫 (cpu_test_db, memory_test_db, disk_test_db)
- 設定使用者權限
- 確認容器間連接

## 📈 預期測試指標

### sysbench輸出指標
- **TPS** (每秒事務數)
- **QPS** (每秒查詢數)
- **平均響應時間**
- **95%、99%百分位響應時間**
- **最小/最大響應時間**
- **錯誤率**

### 系統監控指標
- CPU使用率
- 記憶體使用率
- 磁碟I/O統計
- 網路流量統計

## ⚠️ 實現注意事項

### ARM架構相容性
- MySQL映像檔選擇：`mysql:5.6-arm64v8` 或 `arm64v8/mysql:5.6`
- sysbench映像檔：需要ARM64支援版本
- 測試結果可能與x86架構有差異

### 資源限制
- 總記憶體使用不超過7GB (預留1GB給系統)
- 磁碟空間確保至少15GB可用
- 網路頻寬考量跨EC2延遲

### 安全設定
- MySQL root密碼管理
- 網路埠安全設定
- 測試資料清理機制

## ⏱️ 預估時間
總計約50分鐘完成整個系統實現

---

**建立日期：** 2025-09-27
**版本：** v1.0
**狀態：** 待實現