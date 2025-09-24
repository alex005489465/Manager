# Manager 系統前端應用

## 📋 專案概述

**專案名稱：** Manager 管理系統前端
**版本：** 1.0.0 - 基礎管理功能實現  
**技術架構：** React + TypeScript + Tailwind CSS  
**Node.js版本：** 24.5.0

## 🛠️ 技術棧

- **Framework：** React 19
- **Language：** TypeScript
- **Styling：** Tailwind CSS 4
- **Build Tool：** Vite 7 (前端建置工具)
- **UI Library：** Ant Design 5
- **HTTP Client：** Fetch API (原生)

## 🚀 容器化開發

### 快速開始
```bash
# 1. 啟動Node.js開發服務
cd ../../infra
docker-compose up -d node-dev

# 2. 安裝依賴 (首次使用)
docker exec manager_node_dev npm install

# 3. 啟動React開發服務器 (Vite)
docker exec manager_node_dev npm run dev

# 4. 訪問應用
# http://localhost:3000 - React開發服務器
# http://localhost:8081 - 後端API服務器
```

### 開發除錯
```bash
# 獲取容器名稱 (容器ID會變化)
CONTAINER=$(docker ps --filter "name=manager_node_dev" --format "{{.Names}}")

# 進入容器除錯
docker exec -it $CONTAINER sh

# 查看開發服務器日誌
docker logs $CONTAINER -f

# 重新安裝依賴
docker exec $CONTAINER rm -rf node_modules package-lock.json
docker exec $CONTAINER npm install

# 執行測試
docker exec $CONTAINER npm test

# 建置生產版本
docker exec $CONTAINER npm run build
```

### 容器環境配置
- **Node.js容器：** `manager_node_dev`
- **工作目錄：** `/workspace` (對應本機 `frontend/`)
- **快取目錄：** `./volume/node-dev/`
- **環境變數：** 開發模式、API URL自動配置
- **端口配置：** Vite 必須運行在端口 3000，設置 `strictPort: true` 避免端口衝突錯亂

### ⚠️ 重要注意事項
- **Vite 端口限制：** 開發服務器必須使用端口 3000，不能自動切換到其他端口
- **容器重啟：** 如遇端口衝突，需完全重建容器：`docker-compose down node-dev && docker-compose up -d node-dev`
- **端口衝突處理：** 容器內端口被佔用時，可直接終止佔用進程：`docker exec manager_node_dev pkill -f vite`
- **配置檔案：** `vite.config.ts` 中已設置 `strictPort: true` 強制使用端口 3000

---

**狀態**：🐳 容器化開發環境就緒
**技術就緒**：React + TypeScript + Tailwind CSS + Docker
**最後更新**：2025-09-24
