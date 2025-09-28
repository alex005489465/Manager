#!/bin/bash

# k6 完整性能測試執行腳本
# 依序執行靜態端點和簡單查詢測試

echo "🚀 開始執行完整 k6 性能測試套件..."

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

echo "📍 測試目標: http://${TARGET_HOST}:${TARGET_PORT:-80}"
echo "⏱️  每個測試時長: ${TEST_DURATION:-30s}"
echo "👥 虛擬用戶數: ${VUS:-10}"
echo "📊 目標 RPS: ${RPS:-100}"

# 確保結果目錄存在
mkdir -p k6/results

# 清理舊的結果檔案
echo "🧹 清理舊的測試結果..."
rm -f k6/results/*

# 開始時間記錄
TEST_START=$(date +%s)

echo ""
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo "📊 第一階段：靜態端點 (health) 性能測試"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# 執行靜態端點測試
docker-compose --profile health up --remove-orphans
HEALTH_EXIT_CODE=$?

if [ $HEALTH_EXIT_CODE -eq 0 ]; then
    echo "✅ 靜態端點測試完成"
else
    echo "❌ 靜態端點測試失敗，退出代碼: $HEALTH_EXIT_CODE"
fi

echo ""
echo "⏸️  等待 30 秒讓系統穩定..."
sleep 30

echo ""
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo "🗄️  第二階段：簡單查詢 (query) 性能測試"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# 執行簡單查詢測試
docker-compose --profile query up --remove-orphans
QUERY_EXIT_CODE=$?

if [ $QUERY_EXIT_CODE -eq 0 ]; then
    echo "✅ 簡單查詢測試完成"
else
    echo "❌ 簡單查詢測試失敗，退出代碼: $QUERY_EXIT_CODE"
fi

# 結束時間記錄
TEST_END=$(date +%s)
TEST_DURATION_TOTAL=$((TEST_END - TEST_START))

echo ""
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo "📋 測試完成摘要"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

echo "⏱️  總測試時間: ${TEST_DURATION_TOTAL} 秒"
echo "📍 測試目標: http://${TARGET_HOST}:${TARGET_PORT:-80}"

# 檢查並顯示結果檔案
echo ""
echo "📊 生成的結果檔案:"

if [ $HEALTH_EXIT_CODE -eq 0 ]; then
    echo "   📈 靜態端點測試結果:"
    echo "     ├── JSON: k6/results/health-results.json"
    echo "     ├── HTML: k6/results/health-report.html"
    echo "     └── 摘要: k6/results/health-summary.json"
else
    echo "   ❌ 靜態端點測試：失敗"
fi

if [ $QUERY_EXIT_CODE -eq 0 ]; then
    echo "   🗄️  簡單查詢測試結果:"
    echo "     ├── JSON: k6/results/query-results.json"
    echo "     ├── HTML: k6/results/query-report.html"
    echo "     └── 摘要: k6/results/query-summary.json"
else
    echo "   ❌ 簡單查詢測試：失敗"
fi

# 顯示檔案大小資訊
echo ""
echo "📁 結果檔案詳情:"
ls -lh k6/results/ 2>/dev/null || echo "   (無結果檔案生成)"

# 生成整體測試報告
echo ""
echo "📝 生成整體測試摘要..."
cat > k6/results/overall-summary.json << EOF
{
  "test_suite": "k6-framework-benchmark",
  "test_start": "$(date -d @${TEST_START} --iso-8601)",
  "test_end": "$(date -d @${TEST_END} --iso-8601)",
  "total_duration_seconds": ${TEST_DURATION_TOTAL},
  "target": "http://${TARGET_HOST}:${TARGET_PORT:-80}",
  "configuration": {
    "test_duration": "${TEST_DURATION:-30s}",
    "virtual_users": ${VUS:-10},
    "target_rps": ${RPS:-100}
  },
  "tests": {
    "health_test": {
      "status": "$([ $HEALTH_EXIT_CODE -eq 0 ] && echo 'success' || echo 'failed')",
      "exit_code": $HEALTH_EXIT_CODE
    },
    "query_test": {
      "status": "$([ $QUERY_EXIT_CODE -eq 0 ] && echo 'success' || echo 'failed')",
      "exit_code": $QUERY_EXIT_CODE
    }
  }
}
EOF

echo "✅ 整體摘要已保存到: k6/results/overall-summary.json"

# 最終結果
if [ $HEALTH_EXIT_CODE -eq 0 ] && [ $QUERY_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 所有測試順利完成！"
    exit 0
elif [ $HEALTH_EXIT_CODE -eq 0 ] || [ $QUERY_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "⚠️  部分測試完成，但有測試失敗"
    exit 1
else
    echo ""
    echo "❌ 所有測試都失敗了"
    exit 1
fi