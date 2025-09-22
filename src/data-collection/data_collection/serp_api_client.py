import time
import logging
from typing import Dict, Optional, Any
from serpapi import GoogleSearch
from .config import config

class SerpAPIClient:
    """SerpAPI 客戶端封裝類，用於獲取 Google Maps 評論數據

    使用 SerpAPI 官方 Python 套件簡化實現，提供完整功能：
    - Google Maps 評論數據獲取
    - 自動重試機制
    - 請求頻率控制
    - 完整的錯誤處理和日誌記錄

    Attributes:
        api_key (str): SerpAPI 的 API 金鑰
        logger (logging.Logger): 日誌記錄器
    """
    def __init__(self, api_key: str = None):
        """初始化 SerpAPI 客戶端

        Args:
            api_key (str, optional): SerpAPI 的 API 金鑰。
                如果未提供，將從配置文件中獲取。

        Raises:
            ValueError: 當 API 金鑰未設定時拋出
        """
        # 使用提供的 API 金鑰或從配置中獲取
        self.api_key = api_key or config.SERP_API_KEY

        # 驗證 API 金鑰是否存在
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERP_API_KEY environment variable.")

        # 設定日誌記錄器
        self.logger = logging.getLogger(__name__)

    def get_google_maps_reviews(self, place_id: str, page: int = 1, next_page_token: str = None) -> Optional[Dict[str, Any]]:
        """獲取指定地點的 Google Maps 評論數據

        使用 SerpAPI 官方套件獲取指定 Google Maps 地點的評論數據。
        使用基於 token 的分頁機制，設定語言為繁體中文，並按最新時間排序。

        Args:
            place_id (str): Google Maps 地點的唯一識別碼（data_id）
            page (int, optional): 頁碼（僅用於日誌記錄）。預設為 1。
            next_page_token (str, optional): 分頁令牌，用於獲取後續頁面。

        Returns:
            Optional[Dict[str, Any]]: API 回應的 JSON 數據，包含評論列表和相關元數據。
                如果請求失敗則返回 None。

        Note:
            - 第一頁（無 token）返回 8 條評論
            - 後續頁面最多返回 20 條評論
            - 使用 next_page_token 進行正確的分頁
        """
        # 構建 API 請求參數（使用正確的分頁方式）
        params = {
            'api_key': self.api_key,           # API 認證金鑰
            'engine': 'google_maps_reviews',   # 指定使用 Google Maps 評論引擎
            'data_id': place_id,               # 目標地點的 Google Maps data_id
            'hl': 'zh-TW',                     # 設定語言為繁體中文
            'sort_by': 'newestFirst'           # 按最新時間排序
        }

        # 如果有 next_page_token，添加到參數中
        if next_page_token:
            params['next_page_token'] = next_page_token
            params['num'] = 20                 # 只在有 token 時設定 num 參數

        # 記錄請求開始信息
        self.logger.info(f"發起 API 請求 - 頁數: {page}, place_id: {place_id}")
        start_time = time.time()

        try:
            # 使用 SerpAPI 官方套件發送請求
            search = GoogleSearch(params)
            data = search.get_dict()
            execution_time = time.time() - start_time

            # 統計返回的評論數量
            reviews_count = len(data.get('reviews', []))
            self.logger.info(f"API 請求成功 - 頁數: {page}, 評論數: {reviews_count}, 執行時間: {execution_time:.2f}秒")

            return data

        except Exception as e:
            # 處理所有可能的錯誤（網絡、API、解析等）
            execution_time = time.time() - start_time
            self.logger.error(f"API 請求失敗 - 頁數: {page}, 錯誤: {str(e)}, 執行時間: {execution_time:.2f}秒")
            return None

    def get_reviews_with_retry(self, place_id: str, page: int, next_page_token: str = None) -> Optional[Dict[str, Any]]:
        """帶重試機制的評論數據獲取方法

        這個方法在網絡不穩定或 API 暫時不可用時提供容錯能力。
        會自動重試失敗的請求，每次重試之間有延遲。

        Args:
            place_id (str): Google Maps 地點的唯一識別碼（data_id）
            page (int): 頁碼（僅用於日誌記錄）
            next_page_token (str, optional): 分頁令牌，用於獲取後續頁面

        Returns:
            Optional[Dict[str, Any]]: 成功時返回 API 響應數據，
                所有重試都失敗時返回 None

        Note:
            重試次數和延遲時間在配置文件中設定。
            每次重試前會等待固定的延遲時間。
        """
        # 執行重試邏輯
        for attempt in range(config.MAX_RETRIES):
            try:
                # 嘗試獲取評論數據
                result = self.get_google_maps_reviews(place_id, page, next_page_token)
                if result is not None:
                    return result

                # 如果不是最後一次嘗試，等待後重試
                if attempt < config.MAX_RETRIES - 1:
                    self.logger.warning(f"第 {attempt + 1} 次嘗試失敗，{config.RETRY_DELAY} 秒後重試...")
                    time.sleep(config.RETRY_DELAY)

            except Exception as e:
                # 捕獲所有異常並記錄
                self.logger.error(f"第 {attempt + 1} 次嘗試發生異常: {str(e)}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)

        # 所有重試都失敗
        self.logger.error(f"所有重試嘗試都失敗了 - 頁數: {page}")
        return None

    def add_request_delay(self):
        """在 API 請求之間添加隨機延遲

        為了避免觸發 API 速率限制，在連續請求之間添加隨機延遲。
        延遲時間在配置的最小值和最大值之間隨機選擇。

        Note:
            這是一個重要的禮貌性措施，有助於：
            1. 避免被 API 提供商限制或封鎖
            2. 減少對 SerpAPI 服務的負載
            3. 模擬更自然的使用模式
        """
        import random

        # 生成隨機延遲時間（在配置的範圍內）
        delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
        self.logger.debug(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)