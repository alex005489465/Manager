# Manager 系統 - 後端 API

## 📋 應用概述

**版本：** 0.1.0 - 初始版本  
**技術棧：** Spring Boot 3.5.5 + MySQL + Java 21

## 🚀 快速啟動

```bash
# 1. 啟動Java開發服務
cd ../../infra
docker-compose up -d java-dev

# 2. 啟動應用 (在容器內)
docker exec manager_java_dev mvn spring-boot:run

# 3. 驗證服務
curl http://localhost:8081/actuator/health
```

## 🐛 開發除錯

### 容器環境
- **Java開發容器：** `manager_java_dev` 
- **⚠️ 注意：** 容器ID前綴 `b48b240c93e3_` 會在重啟後改變，需重新獲取
- **獲取容器名：** `docker ps --filter "name=manager_java_dev" --format "{{.Names}}"`
- **進入容器：** `docker exec -it manager_java_dev bash`
- **查看日誌：** `docker logs manager_java_dev`

### API測試端點
```bash
# 系統端點測試
curl http://localhost:8081/                     # 主頁：Manager 系統
curl http://localhost:8081/health               # 健康檢查
curl http://localhost:8081/api/health           # API健康檢查  

# 系統監控
curl http://localhost:8081/actuator/health      # 健康檢查：{"status":"UP"}
curl http://localhost:8081/actuator/info        # 應用資訊：版本、Java版本等
curl http://localhost:8081/actuator/metrics     # 效能指標

# 資料庫連接確認
# Spring Boot啟動日誌應顯示：MySQL 連線成功
# HikariPool-1 連線成功
```

### 常見開發操作
```bash
# 獲取當前容器名 (容器ID會變化)
CONTAINER=$(docker ps --filter "name=manager_java_dev" --format "{{.Names}}")

# 重新編譯
docker exec $CONTAINER mvn clean compile

# 背景啟動應用
docker exec $CONTAINER mvn spring-boot:run &

# 停止應用 (Ctrl+C 或)
docker exec $CONTAINER pkill -f "spring-boot"

# 或直接使用固定容器名 (需手動更新)
docker exec manager_java_dev mvn spring-boot:run
```

## 🔌 API設計

- **模式：** 統一POST請求（非RESTful）
- **路徑：** `POST /api/{module}/{action}`
- **格式：** `{"success": boolean, "data": {}, "message": ""}`

## 📁 專案結構

```
backend/
├── docs/              # 開發文檔
├── src/main/java/     # Java源碼
├── src/main/resources/ # 配置文件
└── src/test/          # 測試程式碼
```

## 🛠 開發工具配置

### 已配置的Maven插件
- **Spotless** - Google Java格式化
- **Checkstyle** - 程式碼風格檢查
- **SpotBugs** - 程式碼問題檢測
- **JaCoCo** - 測試覆蓋率報告

### 程式碼品質檢查
```bash
# 在容器內執行程式碼品質檢查
docker exec $CONTAINER mvn spotless:apply    # 格式化程式碼
docker exec $CONTAINER mvn checkstyle:check  # 風格檢查
docker exec $CONTAINER mvn spotbugs:check    # 問題檢測
docker exec $CONTAINER mvn clean verify      # 完整驗證

# 或直接在容器內檢查Maven配置
docker exec $CONTAINER mvn clean validate
```

### 測試執行
```bash
# 執行測試
docker exec $CONTAINER mvn test

# 生成測試覆蓋率報告
docker exec $CONTAINER mvn jacoco:report
# 報告位置: target/site/jacoco/index.html
```

## 📋 開發工作流程

### 收到設計文件後的開發步驟：

1. **按照設計文件實現流程開發** - 詳見 `docs/開發規範/設計文件實現流程.md`
   - 階段1：解讀設計文件
   - 階段2：規劃實現架構（含@Spec標註）
   - 階段3：對照驗證
   - 階段4：編碼實現
   - 階段5：偏差監控

2. **建立功能模組** - 詳見 `src/README.md` 中的建立步驟

3. **使用Docker容器化環境開發** - 使用上述容器命令進行開發

## ⚠️ 重要提醒

### 開發約束
- **禁用REST規範** - 僅使用GET和POST方法
- **設計文件至上** - 所有實現必須有@Spec標註
- **統一異常處理** - 所有異常回傳HTTP 200
- **規範驗證測試** - 測試要驗證實現與設計文件一致性

### 程式碼品質要求
- **Google Java Style** - 使用Spotless自動格式化
- **Lombok規範使用** - 按照規範文件要求
- **測試覆蓋率** - 整體≥80%，業務邏輯≥90%
- **@Spec標註** - 所有關鍵實現都要有設計文件引用

## 🎯 專案狀態

✅ **專案基礎架構已建立完成**  
✅ **Maven開發工具插件已配置**  
✅ **基礎共用組件已實現**  
✅ **多環境配置檔案已設定**  
✅ **程式碼範例和測試模板已建立**

### 環境配置
- **開發環境** (dev) - MySQL + 詳細日誌
- **測試環境** (test) - H2記憶體資料庫 + 測試配置
- **生產環境** (prod) - 完整資料庫連線池配置

## 📚 開發文檔

詳細開發規範請參考 `docs/開發規範/` 目錄：
- [開發規範總覽](docs/開發規範/README.md)
- [專案結構規範](docs/開發規範/專案結構規範.md) 
- [程式碼風格與品質規範](docs/開發規範/程式碼風格與品質規範.md)
- [設計文件實現流程](docs/開發規範/設計文件實現流程.md)
- [測試策略規範](docs/開發規範/測試策略規範.md)

文檔目錄說明：[docs/README.md](docs/README.md)

程式碼架構說明請參考：[src/README.md](src/README.md)

---

**狀態：** 🎯 Manager 系統基礎架構已就緒，等待功能開發！ 🎉  
**更新：** 2025-09-23