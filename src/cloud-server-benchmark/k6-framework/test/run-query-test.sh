#!/bin/bash

# k6 簡單查詢性能測試執行腳本
# 測試 /api/query 端點的框架 + 資料庫性能

echo "🚀 開始執行簡單查詢 (query) 性能測試..."

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 檔案，請先複製 .env.example 並設定正確的環境變數"
    echo "   cp .env.example .env"
    echo "   vim .env  # 編輯設定 TARGET_HOST 等參數"
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

echo "📍 測試目標: http://${TARGET_HOST}:${TARGET_PORT:-80}/api/query"
echo "⏱️  測試時長: ${TEST_DURATION:-30s}"
echo "👥 虛擬用戶: ${VUS:-10}"
echo "📊 目標 RPS: ${RPS:-100}"
echo "🗄️  注意：此測試需要資料庫連接正常"

# 確保結果目錄存在
mkdir -p k6/results

# 執行測試
echo "🔄 正在執行測試..."
docker-compose --profile query up --remove-orphans

# 檢查測試結果
if [ $? -eq 0 ]; then
    echo "✅ 簡單查詢測試完成"
    echo "📊 結果檔案:"
    echo "   ├── JSON: k6/results/query-results.json"
    echo "   ├── HTML: k6/results/query-report.html"
    echo "   └── 摘要: k6/results/query-summary.json"

    # 顯示結果檔案大小
    ls -lh k6/results/query-* 2>/dev/null || echo "   (結果檔案尚未生成)"
else
    echo "❌ 測試執行失敗"
    exit 1
fi

echo "🏁 測試完成"