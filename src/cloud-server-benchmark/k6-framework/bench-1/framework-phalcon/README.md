# Framework Phalcon

Phalcon 框架實作，用於與 Node.js 框架進行性能比較測試。

## 技術規格

- **PHP**: 8.3
- **框架**: Phalcon 5.8+
- **ORM**: Phalcon Models
- **快取**: OPCache
- **進程管理**: PHP-FPM
- **資料庫**: MySQL

## API 端點

### POST /api/health
健康檢查端點，返回框架狀態。

**回應**:
```json
{
  "status": "OK"
}
```

### POST /api/query
資料庫查詢測試端點。

**請求**:
```json
{
  "id": 123  // 可選，若未提供則使用隨機 ID
}
```

**回應**:
```json
{
  "id": 123,
  "found": true,
  "data": {
    "id": 123,
    "name": "test",
    "value": 456,
    "timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

## 本地開發

```bash
# 安裝依賴
composer install

# 啟動開發伺服器
composer run dev
```

## Docker 部署

使用提供的 Dockerfile 和配置檔案進行容器化部署。

## 環境變數

- `DATABASE_URL`: MySQL 連接字串
- `NODE_ENV`: 執行環境 (production/development)
- `PORT`: 應用程式端口 (預設 3000)