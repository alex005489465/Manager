#!/bin/bash

# MySQL三層次性能測試主腳本
# 執行CPU、Memory、Disk三種不同負載的sysbench測試

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
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

log_step() {
    echo -e "\n${CYAN}${BOLD}=== $1 ===${NC}\n"
}

# 測試配置
MYSQL_USER="${MYSQL_USER:-bench_user}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-bench_pass_2025}"

# MySQL連接設定
MYSQL_HOST_CPU="${MYSQL_HOST_CPU:-localhost}"
MYSQL_HOST_MEMORY="${MYSQL_HOST_MEMORY:-localhost}"
MYSQL_HOST_DISK="${MYSQL_HOST_DISK:-localhost}"
MYSQL_PORT_CPU="${MYSQL_PORT_CPU:-3306}"
MYSQL_PORT_MEMORY="${MYSQL_PORT_MEMORY:-3307}"
MYSQL_PORT_DISK="${MYSQL_PORT_DISK:-3308}"

# 測試參數
TEST_THREADS="${TEST_THREADS:-1,4,16}"
TEST_DURATION="${TEST_DURATION:-180}"

# 測試資料配置
CPU_TABLE_SIZE=100000      # 10萬筆記錄 (~20MB)
MEMORY_TABLE_SIZE=5000000  # 500萬筆記錄 (~1GB)
DISK_TABLE_SIZE=10000000   # 1000萬筆記錄 (~2GB)

# 結果目錄
RESULTS_DIR="/app/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 檢查依賴的函數
check_dependencies() {
    log_info "檢查系統依賴..."

    if ! command -v sysbench &> /dev/null; then
        log_error "sysbench 未安裝"
        exit 1
    fi

    if ! command -v mysql &> /dev/null; then
        log_error "mysql 客戶端未安裝"
        exit 1
    fi

    log_success "系統依賴檢查完成"
}

# 檢查MySQL連接的函數
check_mysql_connection() {
    local host=$1
    local port=$2
    local database=$3
    local test_type=$4

    log_info "檢查 $test_type MySQL連接 (${host}:${port})"

    if mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "SELECT 1;" >/dev/null 2>&1; then
        log_success "$test_type MySQL連接正常"
        return 0
    else
        log_error "$test_type MySQL連接失敗"
        return 1
    fi
}

# 檢查表大小的函數
check_table_size() {
    local host=$1
    local port=$2
    local database=$3
    local test_type=$4

    log_info "檢查 $test_type 測試表大小..."

    local size_info=$(mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        SELECT 
            TABLE_NAME,
            TABLE_ROWS,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS SIZE_MB,
            ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 2) AS SIZE_GB
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = '$database' AND TABLE_NAME = 'sbtest1';
    " 2>/dev/null)

    if [ -n "$size_info" ] && [[ "$size_info" != *"Empty set"* ]]; then
        echo "$size_info" | while read -r line; do
            if [[ "$line" != *"TABLE_NAME"* ]]; then
                log_success "$test_type 測試表資訊: $line"
            fi
        done
    else
        log_warning "$test_type 測試表不存在或為空"
    fi
}

# 獲取表大小資訊用於記錄到文件的函數
get_table_size_info() {
    local host=$1
    local port=$2
    local database=$3

    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        SELECT 
            CONCAT('表名: ', TABLE_NAME),
            CONCAT('記錄數: ', FORMAT(TABLE_ROWS, 0)),
            CONCAT('資料大小: ', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2), ' MB (', ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 / 1024, 3), ' GB)')
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = '$database' AND TABLE_NAME = 'sbtest1';
    " 2>/dev/null | tail -n +2 | tr '\t' '\n'
}

# 準備測試資料的函數
prepare_test_data() {
    local host=$1
    local port=$2
    local database=$3
    local table_size=$4
    local test_type=$5

    log_step "準備 $test_type 測試資料 ($table_size 筆記錄)"

    # 清理現有測試表
    log_info "清理現有測試表..."
    mysql -h"$host" -P"$port" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$database" -e "
        DROP TABLE IF EXISTS sbtest1;
    " 2>/dev/null || true

    # 準備測試資料
    log_info "建立測試資料，預計需要幾分鐘..."
    sysbench oltp_read_only \
        --mysql-host="$host" \
        --mysql-port="$port" \
        --mysql-user="$MYSQL_USER" \
        --mysql-password="$MYSQL_PASSWORD" \
        --mysql-db="$database" \
        --tables=1 \
        --table-size="$table_size" \
        prepare

    if [ $? -eq 0 ]; then
        log_success "$test_type 測試資料準備完成"
        
        # 檢查插入的資料表大小
        check_table_size "$host" "$port" "$database" "$test_type"
    else
        log_error "$test_type 測試資料準備失敗"
        return 1
    fi
}

# 執行單個測試的函數
run_single_test() {
    local host=$1
    local port=$2
    local database=$3
    local threads=$4
    local test_type=$5

    local test_name="${test_type}_${threads}threads"
    local result_file="${RESULTS_DIR}/${test_type,,}-test/${test_name}_${TIMESTAMP}.txt"

    log_info "執行 $test_type 測試 (${threads} 執行緒，${TEST_DURATION} 秒)"

    # 確保結果目錄存在
    mkdir -p "$(dirname "$result_file")"

    # 執行測試並記錄結果
    {
        echo "=== MySQL $test_type 性能測試結果 ==="
        echo "測試時間: $(date)"
        echo "測試類型: $test_type"
        echo "執行緒數: $threads"
        echo "測試時長: $TEST_DURATION 秒"
        echo "目標主機: ${host}:${port}"
        echo "測試資料庫: $database"
        echo "=================================="
        echo
        echo "測試資料表資訊:"
        get_table_size_info "$host" "$port" "$database"
        echo "=================================="
        echo

        sysbench oltp_read_only \
            --mysql-host="$host" \
            --mysql-port="$port" \
            --mysql-user="$MYSQL_USER" \
            --mysql-password="$MYSQL_PASSWORD" \
            --mysql-db="$database" \
            --tables=1 \
            --threads="$threads" \
            --time="$TEST_DURATION" \
            --report-interval=10 \
            run

        echo
        echo "測試完成時間: $(date)"
    } | tee "$result_file"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "$test_name 測試完成，結果儲存至: $result_file"
    else
        log_error "$test_name 測試失敗"
        return 1
    fi
}

# 執行完整測試組的函數
run_test_suite() {
    local host=$1
    local port=$2
    local database=$3
    local table_size=$4
    local test_type=$5

    log_step "開始 $test_type 測試組"

    # 準備測試資料
    prepare_test_data "$host" "$port" "$database" "$table_size" "$test_type"

    # 分割執行緒配置字串並執行測試
    IFS=',' read -ra THREAD_ARRAY <<< "$TEST_THREADS"
    for threads in "${THREAD_ARRAY[@]}"; do
        threads=$(echo "$threads" | tr -d ' ')
        run_single_test "$host" "$port" "$database" "$threads" "$test_type"

        # 測試間等待5秒
        if [ "$threads" != "${THREAD_ARRAY[-1]}" ]; then
            log_info "等待5秒後執行下一個測試..."
            sleep 5
        fi
    done

    # 清理測試資料
    log_info "清理 $test_type 測試資料..."
    sysbench oltp_read_only \
        --mysql-host="$host" \
        --mysql-port="$port" \
        --mysql-user="$MYSQL_USER" \
        --mysql-password="$MYSQL_PASSWORD" \
        --mysql-db="$database" \
        --tables=1 \
        cleanup >/dev/null 2>&1 || true

    log_success "$test_type 測試組完成"
}

# 生成測試摘要的函數
generate_summary() {
    local summary_file="${RESULTS_DIR}/test_summary_${TIMESTAMP}.txt"

    log_info "生成測試摘要..."

    {
        echo "=============================================="
        echo "         MySQL 三層次性能測試摘要"
        echo "=============================================="
        echo "測試時間: $(date)"
        echo "測試配置:"
        echo "  - 執行緒數: $TEST_THREADS"
        echo "  - 每次測試時長: $TEST_DURATION 秒"
        echo "  - CPU測試資料量: $CPU_TABLE_SIZE 筆記錄"
        echo "  - Memory測試資料量: $MEMORY_TABLE_SIZE 筆記錄"
        echo "  - Disk測試資料量: $DISK_TABLE_SIZE 筆記錄"
        echo
        echo "測試結果檔案位置:"
        find "$RESULTS_DIR" -name "*_${TIMESTAMP}.txt" | sort
        echo
        echo "=============================================="
    } > "$summary_file"

    log_success "測試摘要已生成: $summary_file"
}

# 主要執行函數
main() {
    echo
    echo "=============================================="
    echo "          MySQL 三層次性能測試"
    echo "=============================================="
    echo

    # 檢查依賴
    check_dependencies

    # 檢查所有MySQL連接
    log_step "檢查MySQL連接"
    check_mysql_connection "$MYSQL_HOST_CPU" "$MYSQL_PORT_CPU" "cpu_test_db" "CPU" || exit 1
    check_mysql_connection "$MYSQL_HOST_MEMORY" "$MYSQL_PORT_MEMORY" "memory_test_db" "Memory" || exit 1
    check_mysql_connection "$MYSQL_HOST_DISK" "$MYSQL_PORT_DISK" "disk_test_db" "Disk" || exit 1

    # 確保結果目錄存在
    mkdir -p "$RESULTS_DIR"/{cpu-test,memory-test,disk-test}

    # 顯示測試配置
    echo
    log_info "測試配置:"
    echo "  執行緒數: $TEST_THREADS"
    echo "  測試時長: $TEST_DURATION 秒"
    echo "  結果目錄: $RESULTS_DIR"
    echo

    # 開始時間
    TEST_START_TIME=$(date)
    log_info "測試開始時間: $TEST_START_TIME"

    # 執行三層次測試
    run_test_suite "$MYSQL_HOST_CPU" "$MYSQL_PORT_CPU" "cpu_test_db" "$CPU_TABLE_SIZE" "CPU"
    run_test_suite "$MYSQL_HOST_MEMORY" "$MYSQL_PORT_MEMORY" "memory_test_db" "$MEMORY_TABLE_SIZE" "Memory"
    run_test_suite "$MYSQL_HOST_DISK" "$MYSQL_PORT_DISK" "disk_test_db" "$DISK_TABLE_SIZE" "Disk"

    # 結束時間
    TEST_END_TIME=$(date)

    # 生成測試摘要
    generate_summary

    echo
    echo "=============================================="
    log_success "所有測試完成！"
    echo "=============================================="
    echo "開始時間: $TEST_START_TIME"
    echo "結束時間: $TEST_END_TIME"
    echo "結果目錄: $RESULTS_DIR"
    echo
}

# 處理中斷信號
trap 'log_error "測試過程被中斷"; exit 1' INT TERM

# 執行主函數
main "$@"