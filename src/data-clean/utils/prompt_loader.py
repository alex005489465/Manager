"""
Prompt 載入和管理工具

提供 prompt 的載入、管理和版本控制功能
"""

import json
from datetime import datetime
from prompts import (
    get_food_relevance_batch_prompt,
    get_food_relevance_single_prompt,
    get_specific_food_batch_prompt,
    get_specific_food_single_prompt
)
from prompts.food_relevance_prompts import get_prompt_info as get_food_relevance_info
from prompts.specific_food_prompts import get_prompt_info as get_specific_food_info

class PromptLoader:
    """Prompt 載入和管理類別"""

    def __init__(self):
        """初始化 Prompt 載入器"""
        self.prompt_cache = {}
        self.usage_stats = {
            'food_relevance': {'batch': 0, 'single': 0},
            'specific_food': {'batch': 0, 'single': 0}
        }

    def get_food_relevance_prompt(self, review_batch=None, content=None):
        """
        取得食物相關性判別 prompt

        Args:
            review_batch (list): 批次評論列表 [(id, content), ...]
            content (str): 單則評論內容

        Returns:
            str: 格式化後的 prompt
        """
        if review_batch is not None:
            self.usage_stats['food_relevance']['batch'] += 1
            return get_food_relevance_batch_prompt(review_batch)
        elif content is not None:
            self.usage_stats['food_relevance']['single'] += 1
            return get_food_relevance_single_prompt(content)
        else:
            raise ValueError("必須提供 review_batch 或 content 參數")

    def get_specific_food_prompt(self, review_batch=None, content=None, include_examples=True):
        """
        取得具體食物項目判別 prompt

        Args:
            review_batch (list): 批次評論列表 [(id, content), ...]
            content (str): 單則評論內容
            include_examples (bool): 是否包含範例

        Returns:
            str: 格式化後的 prompt
        """
        if review_batch is not None:
            self.usage_stats['specific_food']['batch'] += 1
            return get_specific_food_batch_prompt(review_batch, include_examples)
        elif content is not None:
            self.usage_stats['specific_food']['single'] += 1
            return get_specific_food_single_prompt(content, include_examples)
        else:
            raise ValueError("必須提供 review_batch 或 content 參數")

    def get_prompt_info(self, prompt_type):
        """
        取得 prompt 版本資訊

        Args:
            prompt_type (str): prompt 類型 ('food_relevance' 或 'specific_food')

        Returns:
            dict: prompt 版本資訊
        """
        if prompt_type == 'food_relevance':
            return get_food_relevance_info()
        elif prompt_type == 'specific_food':
            return get_specific_food_info()
        else:
            raise ValueError("不支援的 prompt 類型")

    def get_all_prompt_info(self):
        """
        取得所有 prompt 的版本資訊

        Returns:
            dict: 所有 prompt 的版本資訊
        """
        return {
            'food_relevance': self.get_prompt_info('food_relevance'),
            'specific_food': self.get_prompt_info('specific_food'),
            'last_updated': datetime.now().isoformat()
        }

    def get_usage_stats(self):
        """
        取得 prompt 使用統計

        Returns:
            dict: 使用統計資訊
        """
        total_usage = sum(
            sum(stats.values()) for stats in self.usage_stats.values()
        )

        return {
            'usage_stats': self.usage_stats.copy(),
            'total_calls': total_usage,
            'last_updated': datetime.now().isoformat()
        }

    def reset_usage_stats(self):
        """重置使用統計"""
        self.usage_stats = {
            'food_relevance': {'batch': 0, 'single': 0},
            'specific_food': {'batch': 0, 'single': 0}
        }

    def cache_prompt(self, key, prompt):
        """
        快取 prompt

        Args:
            key (str): 快取鍵值
            prompt (str): prompt 內容
        """
        self.prompt_cache[key] = {
            'prompt': prompt,
            'cached_at': datetime.now().isoformat()
        }

    def get_cached_prompt(self, key):
        """
        取得快取的 prompt

        Args:
            key (str): 快取鍵值

        Returns:
            str or None: 快取的 prompt 內容
        """
        cached = self.prompt_cache.get(key)
        return cached['prompt'] if cached else None

    def clear_cache(self):
        """清除 prompt 快取"""
        self.prompt_cache.clear()

    def export_usage_report(self, filename=None):
        """
        匯出使用報告

        Args:
            filename (str): 報告檔案名稱

        Returns:
            dict: 使用報告
        """
        report = {
            'report_type': 'prompt_usage_report',
            'generated_at': datetime.now().isoformat(),
            'prompt_versions': self.get_all_prompt_info(),
            'usage_statistics': self.get_usage_stats(),
            'cache_status': {
                'cached_prompts': len(self.prompt_cache),
                'cache_keys': list(self.prompt_cache.keys())
            }
        }

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

        return report

class PromptValidator:
    """Prompt 驗證工具"""

    @staticmethod
    def validate_review_batch(review_batch):
        """
        驗證評論批次格式

        Args:
            review_batch (list): 評論批次

        Returns:
            tuple: (is_valid, message)
        """
        if not isinstance(review_batch, list):
            return False, "review_batch 必須是列表"

        if len(review_batch) == 0:
            return False, "review_batch 不能為空"

        for i, item in enumerate(review_batch):
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                return False, f"第 {i+1} 個項目格式錯誤，應為 (id, content) 格式"

            review_id, content = item
            if not isinstance(content, str) or not content.strip():
                return False, f"第 {i+1} 個項目的內容無效"

        return True, "格式正確"

    @staticmethod
    def validate_single_content(content):
        """
        驗證單則評論內容

        Args:
            content (str): 評論內容

        Returns:
            tuple: (is_valid, message)
        """
        if not isinstance(content, str):
            return False, "內容必須是字串"

        if not content.strip():
            return False, "內容不能為空"

        if len(content.strip()) < 3:
            return False, "內容過短，至少需要 3 個字元"

        return True, "內容有效"

# 便利函數
def create_prompt_loader():
    """建立 Prompt 載入器實例"""
    return PromptLoader()

def validate_prompt_input(review_batch=None, content=None):
    """
    驗證 prompt 輸入

    Args:
        review_batch (list): 批次評論列表
        content (str): 單則評論內容

    Returns:
        tuple: (is_valid, message)
    """
    if review_batch is not None:
        return PromptValidator.validate_review_batch(review_batch)
    elif content is not None:
        return PromptValidator.validate_single_content(content)
    else:
        return False, "必須提供 review_batch 或 content 參數"