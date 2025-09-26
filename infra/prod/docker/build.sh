#!/bin/bash

# ================================
# Manager 後端 JAR 打包與導出腳本
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
CONTAINER_NAME="manager_java_dev"
JAR_VERSION="0.1.0"
JAR_NAME="manager-backend-${JAR_VERSION}.jar"
OUTPUT_DIR="java"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Manager 後端 JAR 打包腳本${NC}"
echo -e "${BLUE}================================${NC}"

# 檢查 Docker 是否運行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}錯誤：Docker 未運行，請啟動 Docker 服務${NC}"
    exit 1
fi

# 檢查開發容器是否運行
if ! docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
    echo -e "${RED}錯誤：開發容器 ${CONTAINER_NAME} 未運行${NC}"
    echo -e "${YELLOW}請先啟動開發環境：cd ../../infra && docker-compose up -d java-dev${NC}"
    exit 1
fi

# 建立輸出目錄
echo -e "${YELLOW}準備打包環境...${NC}"
mkdir -p "${OUTPUT_DIR}"

# 清理並重新編譯
echo -e "${YELLOW}清理並編譯專案...${NC}"
docker exec "${CONTAINER_NAME}" mvn clean compile -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 編譯成功${NC}"
else
    echo -e "${RED}❌ 編譯失敗${NC}"
    exit 1
fi

# 執行測試（可選）
read -p "是否要執行測試？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}執行測試...${NC}"
    docker exec "${CONTAINER_NAME}" mvn test -q

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 測試通過${NC}"
    else
        echo -e "${RED}❌ 測試失敗${NC}"
        exit 1
    fi
fi

# 打包 JAR 檔案
echo -e "${YELLOW}打包 JAR 檔案...${NC}"
docker exec "${CONTAINER_NAME}" mvn package -DskipTests=true -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ JAR 打包成功${NC}"
else
    echo -e "${RED}❌ JAR 打包失敗${NC}"
    exit 1
fi

# 檢查 JAR 檔案是否存在
if ! docker exec "${CONTAINER_NAME}" test -f "target/${JAR_NAME}"; then
    echo -e "${RED}錯誤：找不到 JAR 檔案 target/${JAR_NAME}${NC}"
    exit 1
fi

# 複製 JAR 檔案到輸出目錄
echo -e "${YELLOW}導出 JAR 檔案到 ${OUTPUT_DIR}/ 目錄...${NC}"
docker cp "${CONTAINER_NAME}:/workspace/target/${JAR_NAME}" "${OUTPUT_DIR}/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ JAR 檔案導出成功：${OUTPUT_DIR}/${JAR_NAME}${NC}"
    echo -e "${BLUE}檔案大小：$(du -h "${OUTPUT_DIR}/${JAR_NAME}" | cut -f1)${NC}"
else
    echo -e "${RED}❌ JAR 檔案導出失敗${NC}"
    exit 1
fi

# 驗證 JAR 檔案
echo -e "${YELLOW}驗證 JAR 檔案...${NC}"
if java -jar "${OUTPUT_DIR}/${JAR_NAME}" --version >/dev/null 2>&1; then
    echo -e "${GREEN}✅ JAR 檔案驗證成功${NC}"
else
    echo -e "${YELLOW}⚠️  JAR 檔案驗證跳過（需要完整環境）${NC}"
fi

# 建立必要的配置目錄
echo -e "${YELLOW}建立部署目錄結構...${NC}"
mkdir -p volume/mysql
mkdir -p volume/mysql-config
mkdir -p volume/backend-logs

# 詢問是否測試啟動
read -p "是否要測試容器化啟動服務？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}啟動測試環境...${NC}"
    docker-compose up -d

    echo -e "${BLUE}等待服務啟動...${NC}"
    sleep 30

    # 檢查服務狀態
    echo -e "${YELLOW}檢查服務狀態：${NC}"
    docker-compose ps

    # 測試健康檢查端點
    echo -e "${YELLOW}測試健康檢查端點...${NC}"
    if curl -f http://localhost:8083/actuator/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 後端服務健康檢查通過${NC}"
    else
        echo -e "${RED}❌ 後端服務健康檢查失敗${NC}"
        echo -e "${YELLOW}查看日誌：${NC}"
        docker-compose logs manager-backend
    fi

    echo -e "${BLUE}如要停止測試服務，請執行：docker-compose down${NC}"
fi

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}JAR 打包完成！${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "${BLUE}雲端部署檔案清單：${NC}"
echo -e "📁 docker-compose.yml"
echo -e "📁 .env (環境配置)"
echo -e "📁 ${OUTPUT_DIR}/${JAR_NAME}"
echo -e "📁 run.sh (雲端啟動腳本)"
echo -e "📁 volume/ (資料目錄)"

echo -e "${YELLOW}雲端部署步驟：${NC}"
echo -e "1. 複製整個 docker/ 資料夾到雲端"
echo -e "2. chmod +x run.sh"
echo -e "3. ./run.sh"
echo -e ""
echo -e "${GREEN}💡 提示：使用 run.sh 腳本可一鍵啟動服務${NC}"