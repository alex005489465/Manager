# Manager 系統 - 生產環境 JAR 部署

## 🏗️ 工作流程：開發容器打包 → 雲端部署

```
本地環境                   雲端環境
┌─────────────────┐       ┌─────────────────┐
│  開發容器打包    │  →    │  掛載JAR檔案     │
│  導出JAR檔案     │       │  啟動Docker服務  │
└─────────────────┘       └─────────────────┘
```

## 📁 檔案結構

```
infra/prod/docker/
├── Dockerfile              # 生產級構建檔案（備用）
├── docker-compose.yml      # 服務編排（JAR掛載模式）
├── .dockerignore           # 構建優化忽略清單
├── build.sh               # 本地JAR打包與導出腳本
├── run.sh                 # 雲端啟動腳本
├── .env.example           # 環境變數配置範本
├── java/                  # JAR檔案存放目錄
│   └── manager-backend-0.1.0.jar (55MB)
└── README.md              # 部署說明文件
```

## 🚀 本地打包

### 前置條件
- 開發容器 `manager_java_dev` 必須運行中
- 確保後端專案已完成開發

### 1. JAR 打包與導出
```bash
cd infra/prod/docker
chmod +x build.sh
./build.sh
```

打包腳本會：
- ✅ 檢查開發容器狀態
- ✅ 在容器內清理並編譯專案
- ✅ 可選執行測試
- ✅ Maven 打包生成 JAR 檔案
- ✅ 導出 JAR 到 `java/manager-backend-0.1.0.jar`
- ✅ 可選測試容器化啟動

## ☁️ 雲端部署

### 1. 複製檔案到雲端
將整個 `docker/` 資料夾複製到雲端伺服器，確保包含：
- `java/manager-backend-0.1.0.jar` (約55MB)
- `docker-compose.yml`
- `.env.example` → 複製為 `.env` 並配置

### 2. 一鍵啟動服務
```bash
cd docker
chmod +x run.sh
./run.sh
```

啟動腳本會：
- ✅ 檢查 JAR 檔案存在
- ✅ 設定環境變數（如需要）
- ✅ 預拉取 Java 21 運行時鏡像
- ✅ 啟動 MySQL + 後端服務
- ✅ 執行健康檢查和 API 測試
- ✅ 顯示服務狀態

## 🔍 服務端點

- **API 服務**: http://localhost:8082
- **API 健康檢查**: http://localhost:8082/api/health
- **系統健康檢查**: http://localhost:8083/actuator/health
- **監控資訊**: http://localhost:8083/actuator/info
- **資料庫**: localhost:3306

## 📊 技術架構

### JAR 部署模式
- **運行時**: `eclipse-temurin:21-jre-alpine`
- **JAR 檔案**: 透過 Docker Volume 掛載
- **檔案大小**: ~55MB（包含所有依賴）
- **啟動方式**: `java -jar manager-backend-0.1.0.jar`

### 服務組成
- **後端服務**: Spring Boot 3.5.5 JAR 應用
- **資料庫**: MySQL 9.4.0 容器
- **管理工具**: phpMyAdmin（可選）

## 📊 監控與維護

```bash
# 查看服務狀態
docker-compose ps

# 查看後端日誌
docker-compose logs -f manager-backend

# 查看所有日誌
docker-compose logs -f

# 重新啟動後端
docker-compose restart manager-backend

# 重新啟動所有服務
docker-compose restart

# 停止服務
docker-compose down

# 更新 JAR 檔案後重啟
docker-compose restart manager-backend
```

## 🛡️ 安全注意事項

1. **密碼安全**: 修改 .env 中的預設密碼
2. **檔案權限**: JAR 檔案設為唯讀掛載
3. **防火牆**: 僅開放必要端口對外
4. **SSL**: 建議使用反向代理配置 HTTPS
5. **備份**: 定期備份 volume/mysql 資料

## 🔄 更新流程

1. 本地修改程式碼
2. 執行 `./build.sh` 重新打包
3. 複製新的 `java/manager-backend-0.1.0.jar` 到雲端
4. 雲端執行 `docker-compose restart manager-backend`

---

**優勢**: JAR 檔案小、部署快速、資源占用少
**適用**: 中小型專案、快速迭代環境