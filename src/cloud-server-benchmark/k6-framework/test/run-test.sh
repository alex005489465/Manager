#!/bin/bash

# k6 性能測試統一執行腳本
# 自動執行所有測試場景：2端點 × 3負載 = 6個測試

echo "🚀 開始k6性能測試 (2端點 × 3負載)"

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 檔案，請先設定 TARGET_HOST"
    echo "   cp .env.example .env"
    echo "   編輯 .env 設定 TARGET_HOST"
    exit 1
fi

# 載入環境變數
set -a
source .env
set +a

# 檢查必要的環境變數
if [ -z "$TARGET_HOST" ]; then
    echo "❌ 錯誤：TARGET_HOST 環境變數未設定"
    exit 1
fi

echo "📍 目標: http://${TARGET_HOST}:8080"

# 檢查k6容器是否運行
if ! docker ps | grep -q "k6-test"; then
    echo "🔄 啟動k6容器..."
    docker-compose up -d
    sleep 3
fi

# 確保結果目錄存在
docker exec k6-test mkdir -p /results

# 測試場景定義
tests=(
    "health-test.js:load100:Health 100用戶"
    "health-test.js:load200:Health 200用戶"
    "health-test.js:load400:Health 400用戶"
    "query-test.js:load100:Query 100用戶"
    "query-test.js:load200:Query 200用戶"
    "query-test.js:load400:Query 400用戶"
)

total=${#tests[@]}
current=0

# 執行所有測試
for test in "${tests[@]}"; do
    current=$((current + 1))

    # 解析測試參數
    IFS=':' read -r script load_type description <<< "$test"

    echo ""
    echo "▶️  [$current/$total] $description 測試..."

    # 修改config.js中的負載配置
    docker exec k6-test sed -i "s/stages: config\.stages\.[^,]*/stages: config.stages.$load_type/" /scripts/$script

    # 執行k6測試，設置TEST_NAME環境變數
    test_name="${script%.*}-$load_type"
    if docker exec -e TEST_NAME="$test_name" k6-test k6 run /scripts/$script > /dev/null 2>&1; then
        echo "✅ 完成"
    else
        echo "❌ 失敗"
    fi

    # 測試間短暫休息
    sleep 2
done

echo ""
echo "🏁 所有測試完成"
echo "📊 結果文件位於 k6/results/ 目錄"