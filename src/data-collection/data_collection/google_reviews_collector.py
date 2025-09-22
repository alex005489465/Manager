import logging
from typing import Dict, Optional, Any
from .config import config
from .serp_api_client import SerpAPIClient
from .data_storage import DataStorage
from .collection_stats import CollectionStats, StatsReporter
from .logger_setup import get_logger

class GoogleReviewsCollector:
    """Google 評論收集器主類

    重構後的收集器專注於純粹的收集協調邏輯，使用依賴注入的方式
    整合各個專門的組件：
    - SerpAPIClient: API 請求處理
    - DataStorage: 檔案操作管理
    - CollectionStats: 統計數據管理
    - StatsReporter: 報告生成

    職責單一：只負責協調收集流程，不處理具體的檔案操作或統計計算。

    Attributes:
        client (SerpAPIClient): API 客戶端實例
        storage (DataStorage): 數據儲存管理器
        stats_reporter (StatsReporter): 統計報告生成器
        logger (logging.Logger): 日誌記錄器
    """
    def __init__(self, api_key: str = None, storage: DataStorage = None,
                 stats_reporter: StatsReporter = None):
        """初始化 Google 評論收集器

        Args:
            api_key (str, optional): SerpAPI 的 API 金鑰
            storage (DataStorage, optional): 數據儲存管理器，如果未提供則創建新實例
            stats_reporter (StatsReporter, optional): 統計報告生成器，如果未提供則創建新實例
        """
        # 初始化各個組件
        self.client = SerpAPIClient(api_key)
        self.storage = storage or DataStorage()
        self.stats_reporter = stats_reporter or StatsReporter()

        # 設定日誌記錄器（假設日誌系統已經在外部初始化）
        self.logger = get_logger(__name__)

    def collect_reviews(self, place_id: str, start_page: int = 1, max_pages: int = None) -> Dict[str, Any]:
        """收集指定地點的 Google Maps 評論

        重構後的核心方法，專注於協調各個組件完成收集流程。
        使用依賴注入的組件來處理具體的檔案操作和統計管理。

        Args:
            place_id (str): Google Maps 地點的唯一識別碼
            start_page (int, optional): 開始收集的頁碼。預設為 1。
            max_pages (int, optional): 最大收集頁數

        Returns:
            Dict[str, Any]: 收集結果統計（通過 CollectionStats.to_dict() 返回）

        Note:
            此方法會自動跳過已存在的文件，支援斷點續傳。
            每次 API 請求之間會有合適的延遲，避免觸發限制。
        """
        # 設定預設最大頁數
        if max_pages is None:
            max_pages = config.MAX_PAGES

        self.logger.info(f"開始收集評論 - 地點ID: {place_id}")
        self.logger.info(f"頁數範圍: {start_page} - {start_page + max_pages - 1}")

        # 初始化統計數據
        stats = CollectionStats()

        # 使用基於 token 的分頁收集評論
        current_page = start_page
        next_page_token = None
        pages_collected = 0

        while pages_collected < max_pages:
            self.logger.info(f"處理第 {current_page} 頁...")
            stats.add_requested_page()

            # 檢查是否已存在（支援斷點續傳）
            if self.storage.page_already_exists(current_page):
                self.logger.info(f"第 {current_page} 頁已存在，跳過")
                # 從已存在檔案讀取評論數量來更新統計
                existing_data = self.storage.get_page_data(current_page)
                if existing_data:
                    reviews_count = len(existing_data.get('reviews', []))
                    stats.add_successful_page(reviews_count)
                current_page += 1
                pages_collected += 1
                continue

            # 從 API 獲取數據（帶重試機制和 token）
            data = self.client.get_reviews_with_retry(place_id, current_page, next_page_token)

            if data is not None:
                # 數據獲取成功，嘗試保存
                saved_file = self.storage.save_page_data(current_page, data)
                if saved_file:
                    # 保存成功，更新統計
                    reviews_count = len(data.get('reviews', []))
                    stats.add_successful_page(reviews_count, saved_file)

                    self.logger.info(f"第 {current_page} 頁保存成功，評論數: {reviews_count}")

                    # 檢查是否有下一頁的 token
                    serpapi_pagination = data.get('serpapi_pagination', {})
                    next_page_token = serpapi_pagination.get('next_page_token')

                    if not next_page_token:
                        self.logger.info("已到達最後一頁，結束收集")
                        break
                else:
                    # 保存失敗
                    stats.add_failed_page()
                    self.logger.error(f"第 {current_page} 頁保存失敗")
            else:
                # 數據獲取失敗
                stats.add_failed_page()
                self.logger.error(f"第 {current_page} 頁數據獲取失敗")

            current_page += 1
            pages_collected += 1

            # 在非最後一次請求後添加延遲
            if pages_collected < max_pages and next_page_token:
                self.client.add_request_delay()

        # 生成並記錄統計報告
        self.stats_reporter.log_collection_summary(stats)
        return stats.to_dict()

    # 便利方法：委派給 storage 組件
    def get_existing_pages(self):
        """獲取已存在的評論數據文件的頁碼列表

        委派給 DataStorage 組件處理。

        Returns:
            List[int]: 已存在文件的頁碼列表
        """
        return self.storage.get_existing_pages()

    def find_next_missing_page(self) -> int:
        """找出下一個缺失的頁碼

        委派給 DataStorage 組件處理。

        Returns:
            int: 下一個需要收集的頁碼
        """
        return self.storage.find_next_missing_page()

    def get_total_reviews_count(self) -> int:
        """計算已收集的總評論數量

        委派給 DataStorage 組件處理。

        Returns:
            int: 總評論數量
        """
        return self.storage.get_total_reviews_count()