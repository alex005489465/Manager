# 雲伺服器監控系統部署指南

## 📋 系統概述

本監控系統使用 Prometheus + Grafana 架構，提供完整的雲伺服器性能監控解決方案。

### 監控組件
- **本地監控中心**: Prometheus + Grafana + Blackbox Exporter
- **雲端監控代理**: Node Exporter

### 監控範圍
- 系統資源（CPU、記憶體、磁碟、網路）
- 網路連通性和服務可用性

## 🚀 快速部署

### 準備工作

1. **確認本地環境**
   - Docker Desktop 已安裝並運行
   - 確保 9090、3000、9115 端口可用

2. **準備雲端伺服器信息**
   - bench-1 IP 地址
   - test IP 地址
   - bench-2 IP 地址


### 步驟 1: 配置監控目標

⚠️ **重要：必須替換 IP 地址**

編輯 `prometheus/prometheus.yml`，將所有 `bench-1-ip`、`test-ip`、`bench-2-ip` 替換為實際 IP：

```yaml
# 需要替換的位置（已有註解標示）：
static_configs:
  - targets:
      - '192.168.1.10:9100'  # bench-1 實際 IP
      - '192.168.1.11:9100'  # test 實際 IP
      - '192.168.1.12:9100'  # bench-2 實際 IP
```

同時還需要替換：
- HTTP 探測目標：`http://bench-1-ip` → `http://192.168.1.10`
- TCP 探測目標：`bench-1-ip:22` → `192.168.1.10:22`
- ICMP 探測目標：`bench-1-ip` → `192.168.1.10`

### 步驟 2: 啟動本地監控中心

```bash
# 在 monitoring 目錄下執行
docker-compose up -d
```

驗證服務啟動：
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Blackbox Exporter: http://localhost:9115

### 步驟 3: 部署雲端監控代理

將 `exporters/docker-compose.cloud.yml` 複製到各台雲端伺服器：

**所有節點 (bench-1, test, bench-2):**
```bash
# 部署系統監控
docker-compose -f docker-compose.cloud.yml up -d node-exporter

# 驗證服務狀態
docker ps
docker logs node-exporter
```

### 步驟 4: 驗證監控數據

1. **檢查 Prometheus 目標狀態**
   - 訪問 http://localhost:9090/targets
   - 確認所有目標狀態為 "UP"

2. **查看 Grafana 儀表板**
   - 訪問 http://localhost:3000
   - 檢查預設儀表板是否顯示數據

## 📊 儀表板說明

系統提供 2 個預設儀表板：

### 1. 系統資源監控 (system-overview.json)
- CPU 使用率
- 記憶體使用率
- 磁碟使用率
- 網路流量
- 系統負載

### 2. 網路連通性監控 (network-overview.json)
- 服務可用性
- HTTP 回應時間
- TCP 連接時間
- ICMP Ping 延遲
- SSL 證書到期時間

## 🔧 進階配置

### 調整監控頻率

編輯 `prometheus/prometheus.yml`：
```yaml
global:
  scrape_interval: 15s  # 調整全域抓取間隔
```

### 添加告警規則

在 `prometheus/rules/` 目錄下創建告警規則文件：
```yaml
# alerts.yml
groups:
  - name: server.rules
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率過高"
```

### 自定義儀表板

1. 在 Grafana 中創建新儀表板
2. 配置完成後匯出 JSON
3. 將 JSON 文件放入 `grafana/dashboards/` 目錄

## 🛠️ 故障排除

### 常見問題

**1. Prometheus 無法抓取數據**
```bash
# 檢查網路連通性
telnet <target-ip> <port>

# 檢查防火牆設定
sudo ufw status
```

**2. MySQL Exporter 連接失敗**
```bash
# 檢查 MySQL 用戶權限
mysql -u exporter -p -e "SHOW GRANTS;"

# 檢查連接字串
docker logs mysql-exporter
```

**3. Grafana 儀表板無數據**
- 檢查 Prometheus 資料源配置
- 確認時間範圍設定
- 檢查查詢語法

### 監控端口說明

| 服務 | 端口 | 說明 |
|------|------|------|
| Prometheus | 9090 | 監控數據查詢 |
| Grafana | 3000 | 視覺化儀表板 |
| Blackbox Exporter | 9115 | 網路探測 |
| Node Exporter | 9100 | 系統監控 |

## 📝 維護建議

### 定期維護任務

1. **清理舊數據** (每月)
   ```bash
   # Prometheus 自動保留 30 天數據
   # 可調整 docker-compose.yml 中的 --storage.tsdb.retention.time
   ```

2. **備份配置** (每週)
   ```bash
   tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz monitoring/
   ```

3. **檢查磁碟空間** (每週)
   ```bash
   docker system df
   docker volume ls
   ```

### 性能優化

- 根據實際需求調整抓取間隔
- 定期檢查並優化 PromQL 查詢
- 監控 Prometheus 記憶體使用量

## 📞 技術支援

如遇到問題，請檢查：
1. Docker 容器狀態：`docker-compose ps`
2. 服務日誌：`docker-compose logs <service-name>`
3. 網路連通性：`telnet <ip> <port>`
4. 防火牆設定：確保監控端口已開放

---

**部署完成！** 你現在擁有一套完整的雲伺服器監控系統。