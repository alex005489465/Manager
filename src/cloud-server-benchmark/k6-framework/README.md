# k6 框架性能測試

基於 k6 的分散式性能測試框架，使用 **Prisma ORM** 和 **PM2** 進程管理，用於評估 Web 框架在不同場景下的性能表現。

## 技術堆疊

- **框架**: Express.js + Node.js 18
- **ORM**: Prisma 5.6.0
- **進程管理**: PM2 5.3.0 (集群模式)
- **資料庫**: MySQL 8.0
- **測試工具**: k6
- **部署**: Docker + Docker Compose

## 🎯 測試目標

- **靜態端點測試** (`/api/health`)：測試純框架性能，不涉及資料庫操作
- **簡單查詢測試** (`/api/query`)：測試框架 + 資料庫的整體性能
- **主要指標**：RPS (每秒請求數)、響應時間 (ms)、錯誤率

## 🏗️ 架構設計

```
EC2-1 (bench-1)              EC2-2 (bench-2)              EC2-3 (test)
├── nginx (容器)              ├── mysql (容器)              ├── k6 (容器)
└── framework (容器)          └── docker-compose.yml       └── docker-compose.yml
    └── docker-compose.yml
```

## 📁 專案結構

```
k6-framework/
├── bench-1/                     # EC2-1: nginx + framework
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── nginx/
│   │   └── nginx.conf
│   └── framework/
│       ├── Dockerfile
│       ├── package.json
│       └── src/index.js
├── bench-2/                     # EC2-2: mysql
│   ├── docker-compose.yml
│   ├── .env.example
│   └── mysql/
│       ├── init.sql
│       └── my.cnf
├── test/                        # EC2-3: k6 測試
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── run-health-test.sh
│   ├── run-query-test.sh
│   ├── run-all-tests.sh
│   └── k6/
│       ├── scripts/
│       │   ├── config.js
│       │   ├── health-test.js
│       │   └── query-test.js
│       └── results/
└── README.md
```

## 🚀 快速開始

### 1. 環境準備

在每個 EC2 實例上：

```bash
# 安裝 Docker 和 Docker Compose
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 部署順序

#### EC2-2 (bench-2): 啟動 MySQL

```bash
cd bench-2/
cp .env.example .env
# 編輯 .env 設定資料庫密碼
vim .env

docker-compose up -d
docker-compose logs -f mysql  # 等待啟動完成
```

#### EC2-1 (bench-1): 啟動 Framework

```bash
cd bench-1/
cp .env.example .env
# 編輯 .env 設定 EC2-2 的 IP
vim .env  # 設定 DATABASE_HOST=<EC2-2-PRIVATE-IP>

docker-compose up -d
docker-compose logs -f  # 檢查啟動狀態
```

#### EC2-3 (test): 執行測試

```bash
cd test/
cp .env.example .env
# 編輯 .env 設定 EC2-1 的 IP
vim .env  # 設定 TARGET_HOST=<EC2-1-PRIVATE-IP>

# 給執行腳本權限
chmod +x *.sh

# 執行單一測試
./run-health-test.sh   # 靜態端點測試
./run-query-test.sh    # 簡單查詢測試

# 或執行完整測試套件
./run-all-tests.sh
```

## 📊 測試結果

測試完成後，結果會保存在 `test/k6/results/` 目錄：

```
k6/results/
├── health-results.json      # 靜態端點 JSON 結果
├── health-report.html       # 靜態端點 HTML 報告
├── health-summary.json      # 靜態端點摘要
├── query-results.json       # 查詢端點 JSON 結果
├── query-report.html        # 查詢端點 HTML 報告
├── query-summary.json       # 查詢端點摘要
└── overall-summary.json     # 整體測試摘要
```

### 下載結果到本地

```bash
# 從 EC2-3 下載結果
scp -i your-key.pem ec2-user@<EC2-3-IP>:~/k6-framework/test/k6/results/* ./local-analysis/
```

## ⚙️ 配置說明

### 環境變數

**bench-1 (.env)**:
```bash
DATABASE_HOST=<EC2-2-PRIVATE-IP>
DATABASE_PORT=3306
DATABASE_NAME=benchdb
DATABASE_USER=benchuser
DATABASE_PASSWORD=benchpass
```

**bench-2 (.env)**:
```bash
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=benchdb
MYSQL_USER=benchuser
MYSQL_PASSWORD=benchpass
```

**test (.env)**:
```bash
TARGET_HOST=<EC2-1-PRIVATE-IP>
TARGET_PORT=80
TEST_DURATION=30s
VUS=10
RPS=100
DEBUG=false
```

### 測試參數調整

修改 `test/.env` 中的參數：

- `TEST_DURATION`: 測試持續時間 (如: `60s`, `5m`)
- `VUS`: 虛擬用戶數 (並發數)
- `RPS`: 目標每秒請求數
- `DEBUG`: 啟用詳細日誌 (`true`/`false`)

## 🔧 故障排除

### 常見問題

1. **資料庫連接失敗**
   ```bash
   # 檢查 MySQL 容器狀態
   docker-compose ps
   docker-compose logs mysql

   # 檢查網路連接
   telnet <EC2-2-IP> 3306
   ```

2. **測試無法連接到框架**
   ```bash
   # 檢查框架服務狀態
   curl http://<EC2-1-IP>/api/health

   # 檢查 nginx 狀態
   docker-compose logs nginx
   ```

3. **測試結果檔案未生成**
   ```bash
   # 檢查 k6 容器日誌
   docker-compose logs

   # 檢查權限
   ls -la k6/results/
   ```

### 網路設定檢查清單

- [ ] EC2 安全群組允許相應端口 (80, 3306)
- [ ] 私有 IP 設定正確
- [ ] 容器間網路連通性正常
- [ ] 環境變數設定正確

## 📈 性能指標說明

### 關鍵指標

- **RPS**: 每秒請求數，衡量吞吐量
- **P95 響應時間**: 95% 請求的響應時間
- **P99 響應時間**: 99% 請求的響應時間
- **錯誤率**: HTTP 4xx/5xx 錯誤比例

### 預期表現

- **靜態端點**: 高 RPS，低延遲 (< 200ms avg)
- **查詢端點**: 較低 RPS，較高延遲 (< 500ms avg)

## 📄 授權

此專案遵循 MIT 授權條款。