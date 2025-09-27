# MySQL 5.6 + sysbench 測試計劃

## 🏗️ 測試架構設計

### 實例分配
- **bench-1:** 三個MySQL 5.6 Docker容器 (CPU/記憶體/磁碟測試)
- **test:** sysbench Docker 容器 (測試執行節點)
- **bench-2:** 備用 (暫不使用)

### 網路架構
test節點(EC2)通過網際網路連接bench-1節點(EC2)上的三個MySQL容器：
- test → bench-1:3306 (MySQL-CPU容器)
- test → bench-1:3307 (MySQL-Memory容器)
- test → bench-1:3308 (MySQL-Disk容器)

## 🐳 Docker 容器規劃

### 三個MySQL 5.6 容器配置

**MySQL-CPU容器 (port 3306)**
- 用途：CPU密集測試
- Buffer Pool：6G (大記憶體緩存)
- 資料庫：cpu_test_db
- 目標：所有資料都在記憶體中，純測CPU性能

**MySQL-Memory容器 (port 3307)**
- 用途：記憶體壓力測試
- Buffer Pool：512M (中等記憶體緩存)
- 資料庫：memory_test_db
- 目標：部分資料在記憶體，測試記憶體頻寬

**MySQL-Disk容器 (port 3308)**
- 用途：磁碟I/O測試
- Buffer Pool：256M (小記憶體緩存)
- 資料庫：disk_test_db
- 目標：大部分資料需從磁碟讀取，測試I/O性能

### sysbench測試容器 (test節點)
- 安裝sysbench工具
- 掛載測試腳本目錄
- 掛載結果輸出目錄
- 通過bench-1節點的公網IP連接MySQL容器

## 📋 測試項目規劃

### MySQL三層次測試

**Layer 1: CPU密集測試**
- 目標容器：MySQL-CPU (port 3306)
- 測試資料：10萬筆記錄 (~20MB)
- Buffer Pool：6G → 資料100%在記憶體
- 測試類型：純讀取 (oltp_read_only)
- 執行緒數：1, 4, 16
- 測試時間：每個執行緒數3分鐘
- 預期結果：主要測試CPU運算能力

**Layer 2: 記憶體壓力測試**
- 目標容器：MySQL-Memory (port 3307)
- 測試資料：500萬筆記錄 (~1GB)
- Buffer Pool：512M → 資料50-70%在記憶體
- 測試類型：純讀取 (oltp_read_only)
- 執行緒數：1, 4, 16
- 測試時間：每個執行緒數3分鐘
- 預期結果：測試記憶體頻寬與快取效率

**Layer 3: 磁碟I/O測試**
- 目標容器：MySQL-Disk (port 3308)
- 測試資料：5000萬筆記錄 (~10GB)
- Buffer Pool：256M → 資料10-20%在記憶體
- 測試類型：純讀取 (oltp_read_only)
- 執行緒數：1, 4, 16
- 測試時間：每個執行緒數3分鐘
- 預期結果：測試磁碟I/O吞吐量


## ⚙️ MySQL配置要點

### 通用配置
- 連接埠：各容器使用不同port
- 最大連接數：500 (節省記憶體)
- InnoDB刷新策略：每次事務提交刷新
- 查詢快取：關閉 (避免干擾測試)

### 差異化配置
- **CPU容器：** 大log檔案 (512M)，減少I/O
- **Memory容器：** 中log檔案 (256M)
- **Disk容器：** 小log檔案 (128M)，增加I/O壓力

## 🚀 執行流程

### 階段1: 環境準備 (30分鐘)
1. 啟動三個MySQL容器
2. 啟動sysbench容器
3. 網路連通性測試
4. 資料庫初始化確認

### 階段2: MySQL三層次測試 (1.5小時)
1. **Layer 1 (CPU):** 資料準備 + 3個執行緒數測試 (20分鐘)
2. **Layer 2 (Memory):** 資料準備 + 3個執行緒數測試 (35分鐘)
3. **Layer 3 (Disk):** 資料準備 + 3個執行緒數測試 (35分鐘)

### 階段3: 結果分析 (15分鐘)
1. 測試結果收集整理
2. 性能指標對比分析
3. 測試報告生成

## 📊 預期收集指標

### sysbench輸出指標
- **TPS** (每秒事務數)
- **QPS** (每秒查詢數)
- **平均響應時間**
- **95%、99%百分位響應時間**
- **最小/最大響應時間**

## 📁 MySQL測試檔案結構

```
mysql-sysbench/
├── test-plan.md                    # MySQL測試計劃 (本文件)
├── docker/
│   ├── bench-1/
│   │   ├── docker-compose.yml      # 三個MySQL容器配置
│   │   └── mysql-config/           # 各容器的my.cnf配置
│   └── test/
│       └── docker-compose.yml      # sysbench容器配置
├── scripts/
│   └── three-tier-test.sh          # MySQL三層次測試腳本
└── results/                        # MySQL測試結果目錄
```

## ⚠️ 重要注意事項

### ARM架構相容性
- 確保所有Docker映像檔支援ARM64
- 特別注意sysbench工具的ARM版本

### 資源使用估算
- **記憶體：** 三個MySQL容器約需6.8G記憶體
- **磁碟：** Layer 3測試約需15GB可用空間
- **時間：** 完整測試約需2小時

### 網路與安全設定
- **安全群組：** bench-1需開放3306、3307、3308端口給test節點
- **網路延遲：** EC2間網路延遲會影響測試結果，需納入考量
- **防火牆：** 確保EC2間通信順暢

### 測試可靠性
- 每次測試間確實清理資料

---

**總測試時間：** 約2小時
**預期成本：** 0.2556 USD/hour × 2小時 ≈ 0.51 USD