"""Google 評論收集系統主程式

這是重構後的程式入口點，負責：
1. 初始化日誌系統
2. 檢查環境配置
3. 協調各個組件執行收集任務
4. 處理錯誤和異常情況

使用方式：
    python -m data_collection.main
"""

import os
import sys
from .config import config
from .logger_setup import setup_logging
from .google_reviews_collector import GoogleReviewsCollector
from .data_storage import DataStorage
from .collection_stats import StatsReporter


def validate_environment() -> bool:
    """驗證執行環境

    檢查必要的配置和環境變數是否正確設定。

    Returns:
        bool: 如果環境配置正確返回 True，否則返回 False
    """
    errors = []

    # 檢查 API 金鑰
    if not config.SERP_API_KEY:
        errors.append("SERP_API_KEY 未設定或為空")

    # 檢查目標地點 ID
    if not config.TARGET_LOCATION_ID:
        errors.append("TARGET_LOCATION_ID 未設定或為空")

    # 檢查目錄是否可以創建
    try:
        config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"無法創建必要目錄: {e}")

    if errors:
        print("環境配置錯誤:")
        for error in errors:
            print(f"  - {error}")
        print("\n請檢查配置檔案並修正上述問題。")
        return False

    return True


def main():
    """主執行函數

    協調整個收集流程的執行，包括：
    1. 日誌系統初始化
    2. 環境驗證
    3. 組件初始化和依賴注入
    4. 執行收集任務
    5. 結果展示和錯誤處理
    """
    # 初始化日誌系統
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Google 評論收集系統啟動")
    logger.info("=" * 60)

    try:
        # 驗證環境配置
        if not validate_environment():
            sys.exit(1)

        logger.info("環境配置驗證通過")

        # 初始化各個組件
        storage = DataStorage()
        stats_reporter = StatsReporter()
        collector = GoogleReviewsCollector(
            storage=storage,
            stats_reporter=stats_reporter
        )

        logger.info("所有組件初始化完成")

        # 檢查已存在的資料
        existing_pages = collector.get_existing_pages()
        total_existing_reviews = collector.get_total_reviews_count()

        if existing_pages:
            logger.info(f"發現已存在資料: {len(existing_pages)} 頁，共 {total_existing_reviews} 筆評論")
            logger.info(f"已存在頁碼: {existing_pages}")
        else:
            logger.info("未發現已存在資料，將從第 1 頁開始收集")

        # 決定收集策略
        next_page = collector.find_next_missing_page()
        max_pages_to_collect = min(10, config.MAX_PAGES - next_page + 1)

        if max_pages_to_collect <= 0:
            logger.info("已達到最大頁數限制，無需收集更多資料")
            print(f"已收集完成！總共 {total_existing_reviews} 筆評論")
            return

        logger.info(f"計劃從第 {next_page} 頁開始收集，最多收集 {max_pages_to_collect} 頁")

        # 執行收集任務
        stats = collector.collect_reviews(
            place_id=config.TARGET_LOCATION_ID,
            start_page=next_page,
            max_pages=max_pages_to_collect
        )

        # 顯示最終結果
        print("\n" + "=" * 50)
        print("收集任務完成！")
        print(f"本次收集: {stats['total_reviews_collected']} 筆評論")
        print(f"總計評論: {total_existing_reviews + stats['total_reviews_collected']} 筆")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print("=" * 50)

        logger.info("程式執行完成")

    except KeyboardInterrupt:
        logger.info("使用者中斷程式執行")
        print("\n程式已被使用者中斷")
    except Exception as e:
        logger.error(f"程式執行發生錯誤: {str(e)}", exc_info=True)
        print(f"\n程式執行失敗: {str(e)}")
        print("詳細錯誤資訊請查看日誌檔案")
        sys.exit(1)


if __name__ == "__main__":
    main()