#!/bin/bash

# EC2-1 (bench-1) 啟動腳本
# 啟動 nginx + framework (使用 Prisma + PM2)

echo "🚀 啟動 EC2-1 (bench-1) 服務..."

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 檔案，請先複製 .env.example 並設定正確的環境變數"
    echo "   cp .env.example .env"
    echo "   vim .env  # 編輯設定 DATABASE_URL 等參數"
    exit 1
fi

# 載入環境變數
set -a
source .env
set +a

# 檢查必要的環境變數
if [ -z "$DATABASE_URL" ] && [ -z "$DATABASE_HOST" ]; then
    echo "❌ 錯誤：DATABASE_URL 或 DATABASE_HOST 環境變數未設定"
    exit 1
fi

echo "📍 框架端點: http://localhost:8080"
echo "🗄️  資料庫連接: ${DATABASE_URL:-mysql://$DATABASE_USER@$DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME}"
echo "📦 ORM: Prisma"
echo "⚡ 進程管理: PM2"

# 確保日誌目錄存在
mkdir -p framework/logs

echo "🔄 正在啟動服務..."

# 啟動 Docker Compose
docker-compose up -d

# 檢查服務狀態
sleep 10
echo ""
echo "📊 服務狀態檢查:"
docker-compose ps

# 檢查服務健康狀態
echo ""
echo "🔍 健康檢查:"

# 檢查 nginx
if curl -s http://localhost:8080/nginx-health > /dev/null; then
    echo "✅ Nginx: 正常運行"
else
    echo "❌ Nginx: 無法連接"
fi

# 檢查 framework
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "✅ Framework: 正常運行"
else
    echo "❌ Framework: 無法連接"
    echo "   正在檢查 framework 日誌..."
    docker-compose logs --tail=20 framework
fi

# 顯示可用端點
echo ""
echo "📋 可用端點:"
echo "   ├── 健康檢查: http://localhost:8080/api/health"
echo "   ├── 查詢測試: http://localhost:8080/api/query"
echo "   └── Nginx 健康: http://localhost:8080/nginx-health"

echo ""
echo "📝 管理指令:"
echo "   ├── 查看日誌: docker-compose logs -f"
echo "   ├── 重啟服務: docker-compose restart"
echo "   ├── 停止服務: docker-compose down"
echo "   └── PM2 狀態: docker-compose exec framework pm2 status"

echo ""
echo "🎉 EC2-1 (bench-1) 服務啟動完成！"