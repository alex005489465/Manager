import os
import json
from pathlib import Path

class Config:
    """配置管理類

    從 JSON 文件載入配置，支援環境變數覆蓋，提供向下相容的配置接口。
    """

    def __init__(self, config_file: str = None):
        # 系統路徑配置（保留在代碼中）
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data' / 'reviews'
        self.RAW_DATA_DIR = self.DATA_DIR / 'raw'

        # 日誌配置（保留在代碼中）
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        self.LOG_FILE = self.BASE_DIR / 'logs' / 'reviews_collection.log'

        # 載入 JSON 配置
        self._load_json_config(config_file)

        # 確保目錄存在
        self._ensure_directories()

    def _load_json_config(self, config_file: str = None):
        """載入 JSON 配置文件

        Args:
            config_file (str, optional): 配置文件路徑，如果未提供則使用預設路徑
        """
        if config_file is None:
            config_file = Path(__file__).parent / 'config.json'
        else:
            config_file = Path(config_file)

        # 嘗試載入配置文件
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，提供友好的錯誤信息
            example_file = Path(__file__).parent / 'config.json.example'
            raise FileNotFoundError(
                f"配置文件 {config_file} 不存在。\n"
                f"請複製 {example_file} 為 {config_file} 並填入正確的配置值。"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件 {config_file} JSON 格式錯誤: {e}")

        # API 配置
        api_config = config_data.get('api', {})
        self.SERP_API_KEY = os.getenv('SERP_API_KEY', api_config.get('serp_api_key', ''))

        # 目標配置（預設使用永大夜市）
        targets = config_data.get('targets', {})
        default_target = targets.get('永大夜市', {})
        self.TARGET_LOCATION = default_target.get('name', '永大夜市')
        self.TARGET_LOCATION_ID = default_target.get('data_id', '')

        # 收集配置
        collection_config = config_data.get('collection', {})
        self.MAX_PAGES = collection_config.get('max_pages', 50)
        self.REVIEWS_PER_PAGE = collection_config.get('reviews_per_page', 20)
        self.TARGET_REVIEWS_COUNT = collection_config.get('target_reviews_count', 1000)

        # 速率限制配置
        rate_limit_config = config_data.get('rate_limit', {})
        self.REQUEST_DELAY_MIN = rate_limit_config.get('request_delay_min', 2)
        self.REQUEST_DELAY_MAX = rate_limit_config.get('request_delay_max', 3)
        self.MAX_RETRIES = rate_limit_config.get('max_retries', 3)
        self.RETRY_DELAY = rate_limit_config.get('retry_delay', 5)

        # 驗證必要配置
        self._validate_config()

    def _validate_config(self):
        """驗證配置的完整性"""
        errors = []

        if not self.SERP_API_KEY:
            errors.append("SERP_API_KEY 未設定")

        if not self.TARGET_LOCATION_ID:
            errors.append("TARGET_LOCATION_ID 未設定")

        if errors:
            raise ValueError(f"配置驗證失敗: {', '.join(errors)}")

    def _ensure_directories(self):
        """確保必要的目錄存在"""
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    def get_target_config(self, target_name: str = None):
        """獲取指定目標的配置

        Args:
            target_name (str, optional): 目標名稱，如果未提供則使用預設目標

        Returns:
            dict: 包含目標配置的字典
        """
        if target_name is None:
            return {
                'name': self.TARGET_LOCATION,
                'data_id': self.TARGET_LOCATION_ID
            }

        # 可以在這裡擴展支援多個目標
        # 目前只支援預設目標
        return {
            'name': self.TARGET_LOCATION,
            'data_id': self.TARGET_LOCATION_ID
        }

    def get_output_filename(self, page_number: int) -> str:
        return f"yongda_reviews_page_{page_number}.json"

    def get_output_filepath(self, page_number: int) -> Path:
        return self.RAW_DATA_DIR / self.get_output_filename(page_number)

config = Config()