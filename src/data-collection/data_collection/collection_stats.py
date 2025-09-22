import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class CollectionStats:
    """收集任務統計數據類

    使用 dataclass 來管理收集過程中的各種統計信息，
    提供清晰的數據結構和自動生成的基本方法。

    Attributes:
        total_pages_requested (int): 總請求頁數
        successful_pages (int): 成功處理的頁數
        failed_pages (int): 失敗的頁數
        total_reviews_collected (int): 總評論數量
        saved_files (List[str]): 已保存的文件列表
    """
    total_pages_requested: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_reviews_collected: int = 0
    saved_files: List[str] = field(default_factory=list)

    def add_successful_page(self, reviews_count: int, file_path: str = None):
        """記錄成功處理的頁面

        Args:
            reviews_count (int): 該頁面的評論數量
            file_path (str, optional): 保存的文件路徑
        """
        self.successful_pages += 1
        self.total_reviews_collected += reviews_count
        if file_path:
            self.saved_files.append(file_path)

    def add_failed_page(self):
        """記錄失敗的頁面"""
        self.failed_pages += 1

    def add_requested_page(self):
        """記錄請求的頁面"""
        self.total_pages_requested += 1

    def get_success_rate(self) -> float:
        """計算成功率

        Returns:
            float: 成功率百分比，如果沒有請求則返回 0.0
        """
        if self.total_pages_requested == 0:
            return 0.0
        return (self.successful_pages / self.total_pages_requested) * 100

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式

        Returns:
            Dict[str, Any]: 包含所有統計數據的字典
        """
        return {
            'total_pages_requested': self.total_pages_requested,
            'successful_pages': self.successful_pages,
            'failed_pages': self.failed_pages,
            'total_reviews_collected': self.total_reviews_collected,
            'success_rate': self.get_success_rate(),
            'saved_files': self.saved_files.copy()
        }


class StatsReporter:
    """統計報告生成器

    負責生成和記錄收集任務的統計報告，
    將統計數據以易讀的格式輸出到日誌。
    """

    def __init__(self):
        """初始化統計報告生成器"""
        self.logger = logging.getLogger(__name__)

    def log_collection_summary(self, stats: CollectionStats):
        """記錄收集任務的完整總結

        在收集任務完成後記錄詳細的統計信息，包括成功率、
        總評論數量等關鍵指標。

        Args:
            stats (CollectionStats): 收集過程的統計數據
        """
        self.logger.info("=" * 50)
        self.logger.info("收集任務完成總結:")
        self.logger.info(f"總請求頁數: {stats.total_pages_requested}")
        self.logger.info(f"成功頁數: {stats.successful_pages}")
        self.logger.info(f"失敗頁數: {stats.failed_pages}")
        self.logger.info(f"總評論數: {stats.total_reviews_collected}")

        # 計算並顯示成功率
        success_rate = stats.get_success_rate()
        self.logger.info(f"成功率: {success_rate:.1f}%")

        self.logger.info("=" * 50)

    def log_progress_update(self, current_page: int, total_pages: int, stats: CollectionStats):
        """記錄進度更新

        Args:
            current_page (int): 當前頁碼
            total_pages (int): 總頁數
            stats (CollectionStats): 當前統計數據
        """
        progress_percentage = (stats.successful_pages / total_pages) * 100
        self.logger.info(
            f"進度: {stats.successful_pages}/{total_pages} "
            f"({progress_percentage:.1f}%) - "
            f"已收集 {stats.total_reviews_collected} 筆評論"
        )

    def generate_detailed_report(self, stats: CollectionStats) -> Dict[str, Any]:
        """生成詳細的統計報告

        Args:
            stats (CollectionStats): 統計數據

        Returns:
            Dict[str, Any]: 詳細的報告數據
        """
        report = stats.to_dict()

        # 添加額外的分析數據
        if stats.successful_pages > 0:
            avg_reviews_per_page = stats.total_reviews_collected / stats.successful_pages
            report['average_reviews_per_page'] = round(avg_reviews_per_page, 2)
        else:
            report['average_reviews_per_page'] = 0

        # 添加檔案統計
        report['total_files_saved'] = len(stats.saved_files)

        return report