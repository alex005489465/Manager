#!/bin/bash

# MySQL資料庫初始化腳本
# 為三個測試容器初始化資料庫和權限設定

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 預設設定
MYSQL_ROOT_PASSWORD="mysql_bench_2025"
MYSQL_USER="bench_user"
MYSQL_PASSWORD="bench_pass_2025"

# MySQL容器連接設定
MYSQL_HOST_CPU="${MYSQL_HOST_CPU:-localhost}"
MYSQL_HOST_MEMORY="${MYSQL_HOST_MEMORY:-localhost}"
MYSQL_HOST_DISK="${MYSQL_HOST_DISK:-localhost}"
MYSQL_PORT_CPU="${MYSQL_PORT_CPU:-3306}"
MYSQL_PORT_MEMORY="${MYSQL_PORT_MEMORY:-3307}"
MYSQL_PORT_DISK="${MYSQL_PORT_DISK:-3308}"

# 等待MySQL服務啟動的函數
wait_for_mysql() {
    local host=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    log_info "等待MySQL服務 ${host}:${port} 啟動..."

    while [ $attempt -le $max_attempts ]; do
        if mysql -h"$host" -P"$port" -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
            log_success "MySQL服務 ${host}:${port} 已就緒"
            return 0
        fi

        log_info "等待中... (嘗試 $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done

    log_error "MySQL服務 ${host}:${port} 啟動超時"
    return 1
}

# 初始化單個資料庫的函數
init_database() {
    local host=$1
    local port=$2
    local database=$3
    local test_type=$4

    log_info "初始化 $test_type 測試資料庫 ($database) 於 ${host}:${port}"

    # 檢查資料庫連接
    if ! mysql -h"$host" -P"$port" -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
        log_error "無法連接到MySQL服務 ${host}:${port}"
        return 1
    fi

    # 建立資料庫（如果不存在）
    mysql -h"$host" -P"$port" -u root -p"$MYSQL_ROOT_PASSWORD" -e "
        CREATE DATABASE IF NOT EXISTS $database;

        -- 建立測試使用者（如果不存在）
        CREATE USER IF NOT EXISTS '$MYSQL_USER'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';

        -- 授予權限
        GRANT ALL PRIVILEGES ON $database.* TO '$MYSQL_USER'@'%';
        GRANT PROCESS ON *.* TO '$MYSQL_USER'@'%';

        -- 刷新權限
        FLUSH PRIVILEGES;

        -- 確認資料庫建立成功
        USE $database;
        SELECT CONCAT('資料庫 $database 初始化完成') AS result;
    "

    if [ $? -eq 0 ]; then
        log_success "$test_type 測試資料庫初始化完成"
    else
        log_error "$test_type 測試資料庫初始化失敗"
        return 1
    fi
}

# 測試資料庫連接的函數
test_connection() {
    local host=$1
    local port=$2
    local database=$3
    local test_type=$4

    log_info "測試 $test_type 資料庫連接..."

    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        SELECT
            CONNECTION_ID() as connection_id,
            USER() as current_user,
            DATABASE() as current_database,
            VERSION() as mysql_version,
            NOW() as current_time;
    "

    if [ $? -eq 0 ]; then
        log_success "$test_type 資料庫連接測試成功"
    else
        log_error "$test_type 資料庫連接測試失敗"
        return 1
    fi
}

# 主要執行函數
main() {
    echo "============================================"
    echo "          MySQL 資料庫初始化工具"
    echo "============================================"
    echo

    log_info "開始初始化MySQL測試環境..."

    # 等待所有MySQL服務啟動
    wait_for_mysql "$MYSQL_HOST_CPU" "$MYSQL_PORT_CPU" || exit 1
    wait_for_mysql "$MYSQL_HOST_MEMORY" "$MYSQL_PORT_MEMORY" || exit 1
    wait_for_mysql "$MYSQL_HOST_DISK" "$MYSQL_PORT_DISK" || exit 1

    echo
    log_info "所有MySQL服務已啟動，開始初始化資料庫..."
    echo

    # 初始化三個測試資料庫
    init_database "$MYSQL_HOST_CPU" "$MYSQL_PORT_CPU" "cpu_test_db" "CPU" || exit 1
    init_database "$MYSQL_HOST_MEMORY" "$MYSQL_PORT_MEMORY" "memory_test_db" "Memory" || exit 1
    init_database "$MYSQL_HOST_DISK" "$MYSQL_PORT_DISK" "disk_test_db" "Disk" || exit 1

    echo
    log_info "測試所有資料庫連接..."
    echo

    # 測試連接
    test_connection "$MYSQL_HOST_CPU" "$MYSQL_PORT_CPU" "cpu_test_db" "CPU" || exit 1
    test_connection "$MYSQL_HOST_MEMORY" "$MYSQL_PORT_MEMORY" "memory_test_db" "Memory" || exit 1
    test_connection "$MYSQL_HOST_DISK" "$MYSQL_PORT_DISK" "disk_test_db" "Disk" || exit 1

    echo
    echo "============================================"
    log_success "所有資料庫初始化完成！"
    echo "============================================"
    echo
    echo "資料庫連接資訊："
    echo "  CPU測試:    ${MYSQL_HOST_CPU}:${MYSQL_PORT_CPU}/cpu_test_db"
    echo "  Memory測試: ${MYSQL_HOST_MEMORY}:${MYSQL_PORT_MEMORY}/memory_test_db"
    echo "  Disk測試:   ${MYSQL_HOST_DISK}:${MYSQL_PORT_DISK}/disk_test_db"
    echo
    echo "使用者帳號： $MYSQL_USER"
    echo "密碼：       $MYSQL_PASSWORD"
    echo
}

# 處理中斷信號
trap 'log_error "初始化過程被中斷"; exit 1' INT TERM

# 執行主函數
main "$@"