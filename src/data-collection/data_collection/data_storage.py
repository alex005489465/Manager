import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from .config import config


class DataStorage:
    """數據儲存管理類

    負責處理評論數據的檔案操作，包括：
    - JSON 檔案的保存和讀取
    - 檔案存在性檢查
    - 斷點續傳邏輯
    - 已收集頁面的掃描和分析

    這個類專注於檔案系統操作，與 API 收集邏輯分離。
    """

    def __init__(self):
        """初始化數據儲存管理器"""
        self.logger = logging.getLogger(__name__)

    def save_page_data(self, page: int, data: Dict[str, Any]) -> Optional[str]:
        """將指定頁碼的數據保存到 JSON 文件

        將 API 返回的原始數據完整保存到文件中，保持數據的完整性。

        Args:
            page (int): 頁碼
            data (Dict[str, Any]): 要保存的 API 響應數據

        Returns:
            Optional[str]: 成功時返回文件路徑，失敗時返回 None

        Note:
            文件以 UTF-8 編碼保存，並含有縮進格式以便閱讀。
        """
        try:
            filepath = config.get_output_filepath(page)

            # 確保目錄存在
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # 以 UTF-8 編碼寫入 JSON 文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"數據已保存到: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"保存第 {page} 頁數據時發生錯誤: {str(e)}")
            return None

    def page_already_exists(self, page: int) -> bool:
        """檢查指定頁碼的數據文件是否已存在

        這個方法支援斷點續傳功能，避免重複下載已有的數據。

        Args:
            page (int): 要檢查的頁碼

        Returns:
            bool: 如果文件已存在返回 True，否則返回 False
        """
        filepath = config.get_output_filepath(page)
        return filepath.exists()

    def get_existing_pages(self) -> List[int]:
        """獲取已存在的評論數據文件的頁碼列表

        掃描原始數據目錄，找出所有已存在的評論數據文件，
        並提取其頁碼。用於斷點續傳和進度追蹤。

        Returns:
            List[int]: 已存在文件的頁碼列表，按升序排列

        Note:
            只會識別符合命名約定的文件：yongda_reviews_page_*.json
        """
        existing_pages = []

        # 確保目錄存在
        if not config.RAW_DATA_DIR.exists():
            return existing_pages

        # 使用 glob 模式匹配找出所有評論文件
        for file_path in config.RAW_DATA_DIR.glob("yongda_reviews_page_*.json"):
            try:
                # 從文件名中提取頁碼（最後一個下劃線後的數字）
                page_num = int(file_path.stem.split('_')[-1])
                existing_pages.append(page_num)
            except ValueError:
                # 忽略不符合數字格式的文件
                self.logger.warning(f"忽略不符合格式的文件: {file_path}")
                continue

        return sorted(existing_pages)

    def find_next_missing_page(self) -> int:
        """找出下一個缺失的頁碼

        分析已存在的文件，找出第一個缺失的頁碼。
        這個方法支援智能的斷點續傳，在中斷後可以從缺失處繼續。

        Returns:
            int: 下一個需要收集的頁碼

        Examples:
            如果已有 [1, 2, 4, 5]，返回 3
            如果已有 [1, 2, 3]，返回 4
            如果沒有任何文件，返回 1
        """
        existing_pages = self.get_existing_pages()

        # 如果沒有任何文件，從第 1 頁開始
        if not existing_pages:
            return 1

        # 尋找第一個缺失的頁碼
        for i, page in enumerate(existing_pages, 1):
            if page != i:
                return i  # 找到缺失的頁碼

        # 如果沒有缺失，返回下一個連續的頁碼
        return len(existing_pages) + 1

    def get_page_data(self, page: int) -> Optional[Dict[str, Any]]:
        """讀取指定頁碼的數據

        Args:
            page (int): 要讀取的頁碼

        Returns:
            Optional[Dict[str, Any]]: 成功時返回數據，失敗時返回 None
        """
        try:
            filepath = config.get_output_filepath(page)
            if not filepath.exists():
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"讀取第 {page} 頁數據時發生錯誤: {str(e)}")
            return None

    def get_total_reviews_count(self) -> int:
        """計算已收集的總評論數量

        Returns:
            int: 總評論數量
        """
        total_count = 0
        existing_pages = self.get_existing_pages()

        for page in existing_pages:
            data = self.get_page_data(page)
            if data:
                reviews_count = len(data.get('reviews', []))
                total_count += reviews_count

        return total_count