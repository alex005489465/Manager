#!/bin/bash

echo "🚀 Starting Phalcon Framework..."

# 安裝依賴
if [ ! -d "vendor" ]; then
    echo "📦 Installing Composer dependencies..."
    composer install --no-dev --optimize-autoloader
fi

# 檢查環境變數
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: DATABASE_URL not set"
fi

# 啟動 PHP-FPM
echo "🔥 Starting PHP-FPM..."
exec php-fpm