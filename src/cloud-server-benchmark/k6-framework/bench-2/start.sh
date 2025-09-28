#!/bin/bash

# EC2-2 (bench-2) 啟動腳本
# 啟動 MySQL 資料庫服務

echo "🚀 啟動 EC2-2 (bench-2) 資料庫服務..."

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 檔案，請先複製 .env.example 並設定正確的環境變數"
    echo "   cp .env.example .env"
    echo "   vim .env  # 編輯設定資料庫密碼等參數"
    exit 1
fi

# 載入環境變數
set -a
source .env
set +a

# 檢查必要的環境變數
if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    echo "❌ 錯誤：MYSQL_ROOT_PASSWORD 環境變數未設定"
    exit 1
fi

echo "🗄️  資料庫: MySQL 8.0"
echo "📊 資料庫名稱: ${MYSQL_DATABASE:-benchdb}"
echo "👤 用戶名稱: ${MYSQL_USER:-benchuser}"
echo "🔌 端口: 3380 (對外) -> 3306 (容器內)"

echo "🔄 正在啟動 MySQL 資料庫..."

# 啟動 Docker Compose
docker-compose up -d

echo "⏳ 等待 MySQL 啟動中..."
sleep 15

# 檢查服務狀態
echo ""
echo "📊 服務狀態檢查:"
docker-compose ps

# 檢查 MySQL 健康狀態
echo ""
echo "🔍 資料庫健康檢查:"

# 等待 MySQL 完全啟動
attempt=1
max_attempts=12

while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T mysql mysqladmin ping -h localhost > /dev/null 2>&1; then
        echo "✅ MySQL: 正常運行 (嘗試 $attempt/$max_attempts)"
        break
    else
        echo "⏳ MySQL: 正在啟動中... (嘗試 $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ MySQL: 啟動失敗或超時"
    echo "   正在檢查 MySQL 日誌..."
    docker-compose logs --tail=30 mysql
    exit 1
fi

# 檢查資料庫初始化
echo ""
echo "🔍 檢查資料庫初始化狀態:"

if docker-compose exec -T mysql mysql -u${MYSQL_USER:-benchuser} -p${MYSQL_PASSWORD:-benchpass} ${MYSQL_DATABASE:-benchdb} -e "SHOW TABLES;" > /dev/null 2>&1; then
    echo "✅ 資料庫初始化: 完成"

    # 顯示表統計
    table_count=$(docker-compose exec -T mysql mysql -u${MYSQL_USER:-benchuser} -p${MYSQL_PASSWORD:-benchpass} ${MYSQL_DATABASE:-benchdb} -e "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='${MYSQL_DATABASE:-benchdb}';" -s -N 2>/dev/null || echo "0")
    echo "📊 資料表數量: $table_count"

    if [ "$table_count" -gt "0" ]; then
        echo "📋 資料表列表:"
        docker-compose exec -T mysql mysql -u${MYSQL_USER:-benchuser} -p${MYSQL_PASSWORD:-benchpass} ${MYSQL_DATABASE:-benchdb} -e "SHOW TABLES;" 2>/dev/null | grep -v "Tables_in_" | sed 's/^/   ├── /'
    fi
else
    echo "❌ 資料庫初始化: 失敗或未完成"
fi

# 顯示連接資訊
echo ""
echo "🔗 資料庫連接資訊:"
echo "   ├── 主機: $(hostname -I | awk '{print $1}') (私有 IP)"
echo "   ├── 端口: 3380 (對外)"
echo "   ├── 資料庫: ${MYSQL_DATABASE:-benchdb}"
echo "   ├── 用戶: ${MYSQL_USER:-benchuser}"
echo "   └── Prisma URL: mysql://${MYSQL_USER:-benchuser}:${MYSQL_PASSWORD:-benchpass}@$(hostname -I | awk '{print $1}'):3380/${MYSQL_DATABASE:-benchdb}"

echo ""
echo "📝 管理指令:"
echo "   ├── 查看日誌: docker-compose logs -f mysql"
echo "   ├── 進入 MySQL: docker-compose exec mysql mysql -u${MYSQL_USER:-benchuser} -p${MYSQL_PASSWORD:-benchpass} ${MYSQL_DATABASE:-benchdb}"
echo "   ├── 重啟服務: docker-compose restart"
echo "   └── 停止服務: docker-compose down"

echo ""
echo "⚠️  重要提醒："
echo "   請確保 EC2 安全群組開放 3380 端口給 EC2-1"
echo "   請將此 IP 地址設定到 EC2-1 的 DATABASE_HOST 環境變數"

echo ""
echo "🎉 EC2-2 (bench-2) 資料庫服務啟動完成！"