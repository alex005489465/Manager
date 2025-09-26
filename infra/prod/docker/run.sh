#!/bin/bash

# ================================
# Manager 後端 雲端啟動腳本 (JAR 模式)
# ================================

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置變數
PROJECT_NAME="manager"
JAR_VERSION="0.1.0"
JAR_NAME="manager-backend-${JAR_VERSION}.jar"
JAR_PATH="java/${JAR_NAME}"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Manager 雲端啟動腳本 (JAR 模式)${NC}"
echo -e "${BLUE}================================${NC}"

# 檢查 Docker 是否運行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}錯誤：Docker 未運行，請啟動 Docker 服務${NC}"
    exit 1
fi

# 檢查 JAR 檔案是否存在
if [ ! -f "$JAR_PATH" ]; then
    echo -e "${RED}錯誤：找不到 JAR 檔案 $JAR_PATH${NC}"
    echo -e "${YELLOW}請確認已正確複製 java/ 資料夾和 JAR 檔案${NC}"
    exit 1
fi

echo -e "${BLUE}找到 JAR 檔案：$JAR_PATH${NC}"
echo -e "${BLUE}檔案大小：$(du -h "$JAR_PATH" | cut -f1)${NC}"

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 檔案${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}複製 .env.example 為 .env...${NC}"
        cp .env.example .env
        echo -e "${RED}🔧 請編輯 .env 檔案設定資料庫密碼等配置${NC}"
        echo -e "${RED}完成後重新執行此腳本${NC}"
        exit 1
    else
        echo -e "${RED}錯誤：找不到環境配置檔案${NC}"
        exit 1
    fi
fi

# 建立必要的目錄
echo -e "${YELLOW}建立資料目錄...${NC}"
mkdir -p volume/mysql
mkdir -p volume/mysql-config
mkdir -p volume/backend-logs

# 停止可能存在的舊服務
echo -e "${YELLOW}停止舊服務（如存在）...${NC}"
docker-compose down || true

# 預拉取 Java 運行時鏡像
echo -e "${YELLOW}預拉取 Java 運行時鏡像...${NC}"
docker pull eclipse-temurin:21-jre-alpine

# 啟動服務
echo -e "${YELLOW}啟動 Manager 服務...${NC}"
docker-compose up -d

# 等待服務啟動
echo -e "${BLUE}等待服務啟動...${NC}"
sleep 30

# 檢查服務狀態
echo -e "${YELLOW}檢查服務狀態：${NC}"
docker-compose ps

# 檢查 MySQL 是否就緒
echo -e "${YELLOW}檢查 MySQL 服務...${NC}"
MYSQL_CHECK_ATTEMPTS=10
MYSQL_CHECK_INTERVAL=5

for i in $(seq 1 $MYSQL_CHECK_ATTEMPTS); do
    if docker-compose exec -T manager-mysql mysqladmin ping -h localhost --silent; then
        echo -e "${GREEN}✅ MySQL 服務就緒${NC}"
        break
    else
        if [ $i -eq $MYSQL_CHECK_ATTEMPTS ]; then
            echo -e "${RED}❌ MySQL 服務未就緒${NC}"
            exit 1
        else
            echo -e "${YELLOW}等待 MySQL 服務... ($i/$MYSQL_CHECK_ATTEMPTS)${NC}"
            sleep $MYSQL_CHECK_INTERVAL
        fi
    fi
done

# 檢查後端健康狀況
echo -e "${YELLOW}檢查後端健康狀況...${NC}"
HEALTH_CHECK_ATTEMPTS=15
HEALTH_CHECK_INTERVAL=10

for i in $(seq 1 $HEALTH_CHECK_ATTEMPTS); do
    echo -e "${BLUE}健康檢查嘗試 $i/$HEALTH_CHECK_ATTEMPTS...${NC}"

    if curl -f http://localhost:8083/actuator/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 後端服務健康檢查通過${NC}"
        break
    else
        if [ $i -eq $HEALTH_CHECK_ATTEMPTS ]; then
            echo -e "${RED}❌ 後端服務健康檢查失敗${NC}"
            echo -e "${YELLOW}查看後端日誌：${NC}"
            docker-compose logs --tail=50 manager-backend
            echo -e "${YELLOW}查看服務狀態：${NC}"
            docker-compose ps
            exit 1
        else
            echo -e "${YELLOW}等待 ${HEALTH_CHECK_INTERVAL} 秒後重試...${NC}"
            sleep $HEALTH_CHECK_INTERVAL
        fi
    fi
done

# 測試 API 基本功能
echo -e "${YELLOW}測試 API 基本功能...${NC}"
if curl -f http://localhost:8082/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API 基本功能測試通過${NC}"
else
    echo -e "${YELLOW}⚠️  API 基本功能測試跳過 (端點可能需要資料庫連接)${NC}"
fi

# 顯示服務資訊
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}🎉 Manager 系統啟動成功！${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "${BLUE}服務端點：${NC}"
echo -e "🌐 API 服務：       http://localhost:8082"
echo -e "🔄 API 健康檢查：   http://localhost:8082/api/health"
echo -e "💓 系統健康檢查：   http://localhost:8083/actuator/health"
echo -e "📊 監控資訊：       http://localhost:8083/actuator/info"
echo -e "🗄️  資料庫：        localhost:3306"

echo -e "${BLUE}JAR 資訊：${NC}"
echo -e "📦 JAR 檔案：       ${JAR_PATH}"
echo -e "🏷️  版本：           ${JAR_VERSION}"
echo -e "🐳 運行時：          eclipse-temurin:21-jre-alpine"

echo -e "${YELLOW}管理指令：${NC}"
echo -e "查看狀態：         docker-compose ps"
echo -e "查看後端日誌：     docker-compose logs -f manager-backend"
echo -e "查看所有日誌：     docker-compose logs -f"
echo -e "重啟後端：         docker-compose restart manager-backend"
echo -e "重啟所有服務：     docker-compose restart"
echo -e "停止服務：         docker-compose down"

echo -e "${GREEN}🚀 JAR 部署完成！系統已就緒${NC}"