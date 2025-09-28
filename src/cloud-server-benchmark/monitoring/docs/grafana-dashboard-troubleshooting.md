# Grafana 儀表板配置問題排解記錄

## 任務目標
為兩個EC2實例（bench-1和test）創建獨立的Grafana監控儀表板，每個儀表板包含四種核心指標：CPU使用率、記憶體使用率、磁碟使用率、網路流量。

## 遇到的主要問題

### 1. JSON格式錯誤
**問題描述：**
- 初始創建的JSON儀表板使用了錯誤的格式，包裹在 `{"dashboard": {...}}` 結構中
- 這導致Grafana無法正確載入儀表板

**解決方案：**
- 通過Grafana UI的Export功能獲取正確的JSON格式
- 正確格式應該是直接的JSON對象，包含 `annotations`, `panels`, `title` 等頂層屬性
- 移除不必要的wrapper結構

### 2. 數據源配置不一致
**問題描述：**
- JSON中使用小寫的 `"uid": "prometheus"`
- 但實際的數據源配置檔案中名稱為 `"Prometheus"`
- 導致面板顯示 "Datasource prometheus was not found" 錯誤

**解決方案：**
- 檢查 `provisioning/datasources/prometheus.yml` 中的實際數據源名稱
- 統一修正JSON中所有的數據源引用為正確的名稱 `"uid": "Prometheus"`

### 3. Grafana Provisioning配置
**問題描述：**
- 需要確認儀表板是否正確載入到Grafana中

**確認方式：**
- 檢查 `docker-compose.yml` 中的volume掛載：
  - `./grafana/dashboards:/var/lib/grafana/dashboards`
  - `./grafana/provisioning:/etc/grafana/provisioning`
- 確認 `provisioning/dashboards/default.yml` 配置正確

## 解決思路

### 1. 逆向工程方法
- 先檢查已存在且運作正常的bench-1儀表板
- 通過Export功能獲取正確的JSON結構
- 以此為模板創建新的儀表板

### 2. 系統性檢查
1. **服務狀態**: 確認Docker容器都在運行
2. **配置檔案**: 檢查Prometheus和Grafana的配置
3. **數據源**: 驗證數據源名稱和連接
4. **JSON格式**: 使用正確的Grafana schema

### 3. 段階性驗證
- 每修正一個問題後立即測試
- 使用瀏覽器自動化工具驗證結果
- 確保兩個儀表板都能正常顯示數據

## 最終解決方案

### 正確的JSON結構範例
```json
{
  "annotations": {...},
  "editable": true,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "Prometheus"
      },
      "title": "EC2 - CPU 使用率",
      "type": "timeseries",
      ...
    }
  ],
  "refresh": "10s",
  "title": "EC2 指標監控",
  ...
}
```

### 關鍵配置點
1. 數據源UID必須與 `provisioning/datasources/prometheus.yml` 一致
2. 使用完整的Grafana schema結構
3. 確保instance標籤正確對應各EC2的IP和端口
4. 設定適當的刷新間隔和時間範圍

## 經驗總結

### 最佳實踐
1. **優先使用UI Export**: 當不確定JSON格式時，先用Grafana UI創建然後導出
2. **系統性檢查**: 從服務狀態到配置文件，逐層確認
3. **立即驗證**: 每個修改後都要測試，避免累積多個問題
4. **保持一致性**: 確保所有相關配置使用相同的命名約定

### 常見陷阱
- JSON格式包裝器錯誤
- 數據源名稱大小寫不一致
- 缺少必要的schema屬性
- Prometheus查詢表達式中的instance標籤錯誤

---
*記錄時間: 2025-09-28*
*問題解決者: Claude Code*