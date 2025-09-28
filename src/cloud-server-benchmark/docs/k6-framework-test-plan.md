# k6 框架性能測試計劃

## 🎯 測試目標

使用 k6 進行兩個簡單的 API 性能測試：

1. **靜態端點測試**：測試純框架性能，不涉及資料庫操作
2. **簡單查詢測試**：測試框架 + 資料庫的整體性能

主要評估指標：**RPS (每秒請求數)** 和 **響應時間 (ms)**

## 🏗️ 測試架構設計

### Docker Compose 分散部署架構
```
EC2-1 (bench-1)              EC2-2 (bench-2)              EC2-3 (test)
├── nginx (容器)              ├── mysql (容器)              ├── k6 (容器)
└── framework (容器)          └── docker-compose.yml       └── docker-compose.yml
    └── docker-compose.yml

    nginx ←→ framework ←→ mysql ←→ k6 (測試)
```

**部署分配：**
- **EC2-1**：nginx + framework (兩個容器，一個 compose)
- **EC2-2**：mysql (單一容器，一個 compose)
- **EC2-3**：k6 (單一容器，一個 compose)

### 測試 API 設計

1. **靜態端點** (`POST /api/health`)
   - 目標：測試純框架性能
   - 回應：簡單 JSON 響應，不查詢資料庫

2. **簡單查詢** (`POST /api/query`)
   - 目標：測試框架 + 資料庫性能
   - 回應：執行簡單資料庫查詢，涉及資料庫操作

## 📋 測試項目規劃

### 📊 核心測試指標

| 指標 | 說明 |
|------|------|
| **RPS** | 每秒請求數 |
| **響應時間** | 平均、P95、P99 響應時間 (ms) |
| **錯誤率** | HTTP 4xx/5xx 錯誤比例 (%) |

### 🔧 測試腳本

1. **靜態端點測試** (`health-test.js`)
   - 測試 `POST /api/health`
   - 純框架性能，不查詢資料庫

2. **簡單查詢測試** (`query-test.js`)
   - 測試 `POST /api/query`
   - 框架 + 資料庫整體性能

## 🚀 執行流程

### 📅 測試執行步驟

1. **環境準備**
   ```bash
   # EC2-1 (bench-1): 啟動 nginx + framework
   docker-compose up -d

   # EC2-2 (bench-2): 啟動 mysql
   docker-compose up -d

   # 等待所有服務就緒
   docker-compose ps  # 在各自 EC2 上檢查狀態
   ```

2. **執行測試 (在 EC2-3)**
   ```bash
   # 靜態端點測試
   docker-compose run k6 run --out json=/results/health-results.json \
                              --out html=/results/health-report.html \
                              /scripts/health-test.js

   # 簡單查詢測試
   docker-compose run k6 run --out json=/results/query-results.json \
                              --out html=/results/query-report.html \
                              /scripts/query-test.js
   ```

3. **下載結果 (從 EC2-3)**
   ```bash
   # 方法1: 從容器複製到 EC2-3 本地
   docker cp <k6_container_id>:/results/ ./local-results/

   # 方法2: 直接從掛載目錄取得
   scp -i key.pem ec2-user@ec2-3-ip:~/k6-results/* ./local-analysis/
   ```

## 📁 測試專案結構

```
# EC2-1 (bench-1) - nginx + framework
bench-1/
├── docker-compose.yml             # nginx + framework 編排
├── nginx/
│   └── nginx.conf                 # Nginx 配置
└── framework/                     # Web 框架應用代碼
    ├── Dockerfile
    └── src/

# EC2-2 (bench-2) - mysql
bench-2/
├── docker-compose.yml             # mysql 編排
└── mysql/
    ├── init.sql                   # 初始化 SQL
    └── my.cnf                     # MySQL 配置

# EC2-3 (test) - k6
test/
├── docker-compose.yml             # k6 編排
├── k6/
│   ├── scripts/
│   │   ├── health-test.js         # 靜態端點測試
│   │   ├── query-test.js          # 簡單查詢測試
│   │   └── config.js              # 共用配置
│   └── results/                   # 測試結果 (掛載到容器)
│       ├── health-results.json    # 靜態端點 JSON 結果
│       ├── health-report.html     # 靜態端點 HTML 報告
│       ├── query-results.json     # 簡單查詢 JSON 結果
│       └── query-report.html      # 簡單查詢 HTML 報告
```

## ⚠️ 重要注意事項

### 🐳 Docker 環境

1. **跨 EC2 啟動順序**
   - **EC2-2**：先啟動 mysql，等待就緒
   - **EC2-1**：啟動 framework (連接到 EC2-2 mysql)，再啟動 nginx
   - **EC2-3**：執行 k6 測試 (連接到 EC2-1 nginx)

2. **網路連接設定**
   - framework 需配置連接到 EC2-2 的 mysql IP
   - k6 需配置連接到 EC2-1 的 nginx IP
   - 確保 EC2 安全群組開放相應端口

3. **數據持久化**
   - k6 結果掛載到 EC2-3 本地 `./k6/results/` 目錄
   - 測試完成後透過 SCP 下載到本地分析

### 📊 k6 輸出格式

1. **JSON 結果** (`.json`)
   - 包含完整測試數據和指標
   - 核心指標：`http_req_duration`, `http_req_rate`, `http_req_failed`
   - 適合程式化分析和數據處理
   - 可導入到分析工具進行深入研究

2. **HTML 報告** (`.html`)
   - 視覺化圖表和統計摘要
   - 包含響應時間分佈圖、RPS 趨勢圖
   - 自動計算 P90、P95、P99 百分位數
   - 適合快速檢視和分享結果

3. **輸出範例**
   ```bash
   # 測試完成後會生成：
   ./k6/results/health-results.json     # 靜態端點原始數據
   ./k6/results/health-report.html      # 靜態端點可視化報告
   ./k6/results/query-results.json      # 查詢端點原始數據
   ./k6/results/query-report.html       # 查詢端點可視化報告
   ```

### 🔄 測試最佳實務

1. **測試間隔**
   - 兩次測試間等待 30 秒讓系統穩定
   - 確保容器間網路連接正常

2. **結果分析**
   - 靜態端點：預期較高 RPS，較低延遲
   - 查詢端點：預期較低 RPS，較高延遲
   - 手動下載結果到本地進行深入分析

---

**建立日期：** 2025-09-27
**狀態：** 規劃完成