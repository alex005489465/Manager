# phpMyAdmin 主題設定完整指南

## 概述

本文檔記錄了為 phpMyAdmin 5.2 設定多種主題的完整過程，包括暗色主題的安裝、問題排除和最佳實踐。

## 目錄結構

```
infra/
├── docker-compose.yml
├── volume/
│   └── phpmyadmin/
│       └── themes/          # 主題存放目錄
│           ├── original/    # 預設主題
│           ├── bootstrap/
│           ├── metro/
│           ├── pmahomme/
│           ├── blueberry/   # 新增主題
│           ├── boodark/     # 暗色主題系列
│           ├── boodark-nord/
│           ├── boodark-orange/
│           ├── boodark-teal/
│           └── darkwolf/
└── docs/
    └── phpMyAdmin-主題設定指南.md
```

## 問題回顧

### 初始問題
1. **無效的環境變數**：`PMA_THEME: dark` 不存在
2. **版面破壞**：卷掛載覆蓋了原始主題，導致界面混亂
3. **主題選項缺失**：只剩 4 個預設主題可選

### 解決方案

#### 1. 正確的卷掛載設定

```yaml
# docker-compose.yml
services:
  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    container_name: phpmyadmin
    environment:
      PMA_HOST: mysql
      PMA_PORT: 3306
      PMA_USER: root
      PMA_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      UPLOAD_LIMIT: 1024M
      # 注意：不要設定 PMA_THEME，讓用戶自己選擇
    volumes:
      - ./volume/phpmyadmin/themes:/var/www/html/themes
    ports:
      - "${PHPMYADMIN_PORT:-8080}:80"
    networks:
      - app_network
```

#### 2. 主題安裝流程

##### 步驟 1：備份原始主題
```bash
# 停止服務
docker-compose down

# 啟動臨時容器複製原始主題
docker run --name temp_pma -d phpmyadmin/phpmyadmin:latest
docker cp temp_pma:/var/www/html/themes/. ./volume/phpmyadmin/themes/
docker rm -f temp_pma
```

##### 步驟 2：下載第三方主題
```bash
cd volume/phpmyadmin/themes

# Blueberry 主題
curl -L -o blueberry.zip "https://files.phpmyadmin.net/themes/blueberry/1.1.0/blueberry-1.1.0.zip"
unzip blueberry.zip && rm blueberry.zip

# BooDark 暗色系列主題
curl -L -o boodark.zip "https://github.com/adorade/boodark/releases/latest/download/boodark-v1.2.0.zip"
unzip boodark.zip && rm boodark.zip

curl -L -o boodark-nord.zip "https://files.phpmyadmin.net/themes/boodark-nord/1.1.0/boodark-nord-1.1.0.zip"
unzip boodark-nord.zip && rm boodark-nord.zip

curl -L -o boodark-orange.zip "https://files.phpmyadmin.net/themes/boodark-orange/1.1.0/boodark-orange-1.1.0.zip"
unzip boodark-orange.zip && rm boodark-orange.zip

curl -L -o boodark-teal.zip "https://files.phpmyadmin.net/themes/boodark-teal/1.1.0/boodark-teal-1.1.0.zip"
unzip boodark-teal.zip && rm boodark-teal.zip

# Darkwolf 主題
curl -L -o darkwolf.zip "https://files.phpmyadmin.net/themes/darkwolf/5.2/darkwolf-5.2.zip"
unzip darkwolf.zip && rm darkwolf.zip
```

##### 步驟 3：重新啟動服務
```bash
docker-compose up -d
```

## 已安裝主題列表

### 預設主題（4 個）
- **Original** - 經典白色主題
- **Bootstrap** - Bootstrap 風格
- **Metro** - 現代風格主題
- **Pmahomme** - 簡潔主題

### 新增主題（7 個）

#### 暗色主題系列（6 個）
1. **BooDark (Cyan)** - 暗色主題，青色強調
2. **BooDark Nord** - 採用 Nord 配色方案的暗色主題
3. **BooDark Orange** - 橙色配色的暗色主題
4. **BooDark Teal** - 藍綠配色的暗色主題
5. **Darkwolf** - 專為 phpMyAdmin 5.2 設計的暗色主題

#### 亮色主題（1 個）
6. **Blueberry** - 清新藍莓風格主題

### 主題特色

#### BooDark 系列
- **技術基礎**：Bootstrap 5.3.8
- **授權**：MIT License
- **支援版本**：phpMyAdmin 5.2+
- **特色**：
  - 深色背景 + 淺色字體
  - 多種顏色方案選擇
  - 完整的 SVG 圖示支援
  - RTL（右到左）語言支援

#### Darkwolf
- **專為 phpMyAdmin 5.2 設計**
- **現代化暗色設計**
- **混合 PNG 和 SVG 圖示**

#### Blueberry
- **清新明亮的藍色風格**
- **豐富的 SCSS 自訂選項**
- **完整的響應式設計**

## 使用方式

### 切換主題
1. 打開瀏覽器訪問 http://localhost:8080
2. 使用 root 帳號自動登入
3. 點擊右上角的**設定圖示**（齒輪符號）
4. 在左側選單選擇**「主題」**
5. 從 11 種主題中選擇您喜歡的
6. 點擊**「應用」**即可立即生效

### 推薦主題

#### 護眼使用
- **BooDark Nord** - 柔和的藍灰色調
- **BooDark Teal** - 舒適的藍綠色調

#### 專業工作
- **BooDark (Cyan)** - 經典暗色 + 專業青色
- **Darkwolf** - 純正的暗色專業風格

#### 清新風格
- **Blueberry** - 明亮清新的工作環境

## 常見問題與解決方案

### 問題 1：主題選項不出現
**原因**：卷掛載路徑不正確或權限問題

**解決方案**：
```bash
# 檢查掛載是否成功
docker exec phpmyadmin ls -la /var/www/html/themes

# 應該看到所有主題目錄
```

### 問題 2：切換主題後版面破壞
**原因**：主題不相容或檔案損壞

**解決方案**：
```bash
# 重新下載主題
cd volume/phpmyadmin/themes
rm -rf [主題名稱]
# 重新下載並解壓縮主題
```

### 問題 3：連線失敗
**原因**：MySQL 容器還在初始化

**解決方案**：
```bash
# 檢查 MySQL 狀態
docker-compose logs mysql | tail -10

# 等待看到 "ready for connections" 後重啟 phpMyAdmin
docker-compose restart phpmyadmin
```

## 主題開發資源

### 官方資源
- **phpMyAdmin 主題頁面**：https://www.phpmyadmin.net/themes/
- **官方主題 GitHub**：https://github.com/phpmyadmin/themes
- **主題開發文檔**：https://docs.phpmyadmin.net/en/qa_5_2/themes.html

### 第三方主題來源
- **BooDark 系列**：https://github.com/adorade/boodark
- **社區主題**：https://github.com/phpmyadmin/themes

## 維護指南

### 定期檢查
1. **每季檢查**主題更新
2. **測試新版本**的 phpMyAdmin 相容性
3. **備份主題設定**

### 更新流程
```bash
# 1. 備份現有主題
cp -r volume/phpmyadmin/themes volume/phpmyadmin/themes.backup

# 2. 下載新版本主題
# 3. 測試主題功能
# 4. 確認無問題後刪除備份
```

## 最佳實踐

### 1. 主題管理
- 保持原始預設主題不變
- 定期清理未使用的主題
- 記錄自訂主題的來源和版本

### 2. 效能優化
- 選擇輕量級主題（如 Original、Metro）用於生產環境
- 暗色主題可能稍微增加 CSS 載入時間

### 3. 用戶體驗
- 為不同用戶群組推薦合適的主題
- 在團隊中統一使用相同主題風格

## 結論

通過本指南的設定，您的 phpMyAdmin 現在擁有：
- **11 種精選主題**（4 預設 + 7 新增）
- **6 種暗色主題選擇**
- **完整的 phpMyAdmin 5.2 相容性**
- **靈活的主題切換機制**

這套配置為資料庫管理工作提供了豐富的視覺選擇，同時保持了穩定性和效能。

---

**文檔版本**：v1.0
**最後更新**：2025-09-23
**適用版本**：phpMyAdmin 5.2.2, Docker Compose
**維護者**：Claude Code Assistant