# PHP Phalcon 框架整合規劃

## 目標

在現有的 k6 性能測試環境中新增 PHP Phalcon 框架，與 Node.js 框架進行性能比較。

## 現有架構分析

### 當前 bench-1 結構
- **框架**: Node.js + Express + Prisma ORM
- **資料庫**: MySQL
- **反向代理**: Nginx (8080 → 3000)
- **部署**: Docker Compose
- **進程管理**: PM2
- **API 端點**:
  - `POST /api/health` - 健康檢查
  - `POST /api/query` - 資料庫查詢測試

## 重構規劃

### 1. 目錄結構重組

```
bench-1/
├── docker-compose.yml
├── start.sh
├── nginx/
│   └── nginx.conf (更新配置)
├── framework-node/          ← 重命名現有 framework
│   ├── package.json
│   ├── ecosystem.config.js
│   ├── prisma/
│   ├── src/
│   └── logs/
└── framework-phalcon/       ← 新增 Phalcon 框架
    ├── public/
    │   └── index.php
    ├── src/
    │   ├── app/
    │   ├── config/
    │   └── library/
    ├── composer.json
    ├── php-fpm.conf
    └── logs/
```

### 2. 端口配置

- **8080**: Nginx 對外端口 (現有)
- **8081**: Nginx 新增端口 (轉接到 Phalcon)
- **3000**: Node.js 應用端口 (現有)
- **9000**: PHP-FPM 端口 (新增)

### 3. Nginx 配置更新

```nginx
# 8080 端口 - Node.js 框架
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://framework_node_backend;
        # ... 現有配置
    }
}

# 8081 端口 - Phalcon 框架
server {
    listen 8081;
    server_name _;

    location /api/ {
        fastcgi_pass framework_phalcon:9000;
        fastcgi_index index.php;
        # ... PHP-FPM 配置
    }
}
```

### 4. Docker Compose 服務配置

#### 新增 framework-phalcon 服務
```yaml
framework-phalcon:
  image: php:8.3-fpm-alpine
  container_name: bench-framework-phalcon
  working_dir: /app
  volumes:
    - ./framework-phalcon:/app
    - ./framework-phalcon/logs:/app/logs
  environment:
    - PHP_FPM_LISTEN=0.0.0.0:9000
    - DATABASE_URL=${DATABASE_URL}
  networks:
    - bench-network
```

#### 更新 framework 服務
```yaml
framework-node:  # 重命名
  image: node:22-alpine
  container_name: bench-framework-node
  # ... 現有配置
```

### 5. Phalcon 框架實作規格

#### 技術堆疊
- **PHP 版本**: 8.3
- **Phalcon 版本**: 5.8+ (最新穩定版)
- **ORM**: Phalcon Model/PHQL
- **快取**: OPCache + APCu
- **進程管理**: PHP-FPM
- **資料庫**: MySQL (共用現有資料庫)

#### 性能優化配置
```ini
; php.ini 優化
opcache.enable=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=8
opcache.max_accelerated_files=10000
opcache.revalidate_freq=2
opcache.validate_timestamps=0
opcache.save_comments=1
opcache.fast_shutdown=1

; php-fpm.conf 優化
pm = dynamic
pm.max_children = 50
pm.start_servers = 10
pm.min_spare_servers = 5
pm.max_spare_servers = 20
```

#### API 端點實作
需實作與 Node.js 版本相同的 API：

1. **`POST /api/health`**
   ```php
   // 簡單健康檢查，不涉及資料庫
   return $this->response->setJsonContent(['status' => 'OK']);
   ```

2. **`POST /api/query`**
   ```php
   // 根據 ID 查詢 benchmark_test 表
   // 支援隨機 ID 生成
   // 返回格式與 Node.js 版本一致
   ```

### 6. 資料庫配置

- **共用現有 MySQL 實例**
- **表結構**: 使用現有 `benchmark_test` 表
- **連接池**: 配置 Phalcon Database 連接池
- **索引優化**: 確保查詢性能

### 7. 部署流程

1. **重命名現有目錄**
   ```bash
   mv framework framework-node
   ```

2. **創建 Phalcon 應用**
   - 使用 Composer 安裝 Phalcon
   - 配置 MVC 結構
   - 實作 API 控制器

3. **更新 Docker Compose**
   - 新增 Phalcon 服務
   - 更新 Nginx 配置
   - 配置環境變數

4. **測試驗證**
   - 功能測試：確保 API 回應正確
   - 性能基準：運行初始 k6 測試

### 8. 測試比較方案

#### 測試場景
1. **純框架性能**: `/api/health` 端點
2. **資料庫查詢性能**: `/api/query` 端點
3. **併發處理能力**: 不同併發數下的性能表現
4. **記憶體使用**: 監控兩框架的記憶體消耗

#### 比較指標
- **吞吐量** (RPS - Requests Per Second)
- **回應時間** (平均/P95/P99)
- **錯誤率**
- **資源使用** (CPU/Memory)
- **穩定性** (長時間運行)

### 9. 實作時程

1. **階段一** (1-2 天): 目錄重構 + Nginx 配置
2. **階段二** (2-3 天): Phalcon 應用開發
3. **階段三** (1 天): Docker 整合 + 測試
4. **階段四** (1 天): k6 測試腳本調整 + 初始比較

### 10. 風險與注意事項

- **向後相容性**: 確保現有測試腳本仍可正常運行
- **環境一致性**: 兩框架使用相同的系統資源配置
- **資料庫連接**: 避免連接數過多導致資料庫瓶頸
- **快取策略**: 確保測試的公平性，避免快取影響結果

## 執行檢查清單

- [ ] 備份現有 bench-1 配置
- [ ] 重命名 framework → framework-node
- [ ] 建立 framework-phalcon 目錄結構
- [ ] 更新 docker-compose.yml
- [ ] 配置 Nginx 雙端口支援
- [ ] 實作 Phalcon API 端點
- [ ] 測試兩框架功能正確性
- [ ] 執行初始性能比較測試
- [ ] 撰寫測試結果報告

---

*此規劃文件將作為 PHP Phalcon 框架整合的實作指南，確保與現有 Node.js 框架進行公平且全面的性能比較。*