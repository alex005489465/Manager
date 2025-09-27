#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基礎分析器模組

提供所有分析器的基礎抽象類別和共用功能
"""

import pandas as pd
import logging
from abc import ABC, abstractmethod
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import ANALYSIS_CONFIG

# 設定日誌
logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """基礎分析器抽象類別"""

    def __init__(self, dataset):
        """
        初始化基礎分析器

        Args:
            dataset (pd.DataFrame): 核心資料集
        """
        self.dataset = dataset
        self.low_threshold = ANALYSIS_CONFIG['low_rating_threshold']
        self.high_threshold = ANALYSIS_CONFIG['high_rating_threshold']
        self.min_samples_dish = ANALYSIS_CONFIG['min_samples_dish']
        self.min_samples_vendor = ANALYSIS_CONFIG['min_samples_vendor']
        self.top_n = ANALYSIS_CONFIG['top_n_items']

        # 驗證資料集
        self.validate_dataset()

    def validate_dataset(self):
        """驗證輸入資料集的有效性"""
        if self.dataset is None or self.dataset.empty:
            raise ValueError("資料集不能為空")

        required_columns = ['rating', 'business_name']
        missing_columns = [col for col in required_columns if col not in self.dataset.columns]
        if missing_columns:
            raise ValueError(f"資料集缺少必要欄位: {missing_columns}")

        logger.info(f"資料集驗證完成 - 共 {len(self.dataset)} 筆記錄")

    def filter_by_rating_range(self, min_rating=None, max_rating=None):
        """
        按評分範圍過濾資料

        Args:
            min_rating (float): 最低評分
            max_rating (float): 最高評分

        Returns:
            pd.DataFrame: 過濾後的資料集
        """
        filtered_data = self.dataset.copy()

        if min_rating is not None:
            filtered_data = filtered_data[filtered_data['rating'] >= min_rating]

        if max_rating is not None:
            filtered_data = filtered_data[filtered_data['rating'] <= max_rating]

        return filtered_data

    def get_low_rating_data(self):
        """
        取得低評分資料

        Returns:
            pd.DataFrame: 低評分資料
        """
        return self.filter_by_rating_range(max_rating=self.low_threshold)

    def get_high_rating_data(self):
        """
        取得高評分資料

        Returns:
            pd.DataFrame: 高評分資料
        """
        return self.filter_by_rating_range(min_rating=self.high_threshold)

    def calculate_rating_statistics(self, group_column):
        """
        計算評分統計資訊

        Args:
            group_column (str): 分組欄位名稱

        Returns:
            pd.DataFrame: 統計結果
        """
        stats = self.dataset.groupby(group_column).agg({
            'rating': [
                'count',
                'mean',
                lambda x: (x <= self.low_threshold).sum(),
                lambda x: (x >= self.high_threshold).sum()
            ]
        }).round(2)

        # 重新命名欄位
        stats.columns = ['total_count', 'avg_rating', 'low_rating_count', 'high_rating_count']

        # 計算比率
        stats['low_rating_ratio'] = (stats['low_rating_count'] / stats['total_count'] * 100).round(2)
        stats['high_rating_ratio'] = (stats['high_rating_count'] / stats['total_count'] * 100).round(2)

        return stats

    def filter_by_min_samples(self, stats_df, min_samples):
        """
        按最少樣本數過濾統計結果

        Args:
            stats_df (pd.DataFrame): 統計資料
            min_samples (int): 最少樣本數

        Returns:
            pd.DataFrame: 過濾後的統計資料
        """
        return stats_df[stats_df['total_count'] >= min_samples]

    def get_top_n_items(self, stats_df, sort_columns, ascending=None, n=None):
        """
        取得排行榜前N項

        Args:
            stats_df (pd.DataFrame): 統計資料
            sort_columns (list): 排序欄位
            ascending (list): 是否升序排列
            n (int): 取前N項，預設使用配置值

        Returns:
            pd.DataFrame: 排行榜資料
        """
        if n is None:
            n = self.top_n

        if ascending is None:
            ascending = [False] * len(sort_columns)

        return stats_df.sort_values(sort_columns, ascending=ascending).head(n)

    def calculate_opportunity_score(self, stats_df):
        """
        計算商機綜合指數

        Args:
            stats_df (pd.DataFrame): 統計資料

        Returns:
            pd.DataFrame: 包含商機指數的資料
        """
        # 正規化低評分數量和比率 (0-1)
        max_count = stats_df['low_rating_count'].max()
        max_ratio = stats_df['low_rating_ratio'].max()

        if max_count > 0:
            stats_df['normalized_count'] = stats_df['low_rating_count'] / max_count
        else:
            stats_df['normalized_count'] = 0

        if max_ratio > 0:
            stats_df['normalized_ratio'] = stats_df['low_rating_ratio'] / max_ratio
        else:
            stats_df['normalized_ratio'] = 0

        # 商機指數 = 低評分數量 * 低評分比率 (權重各 50%)
        stats_df['opportunity_score'] = (
            stats_df['normalized_count'] * 0.5 +
            stats_df['normalized_ratio'] * 0.5
        ).round(3)

        return stats_df.sort_values('opportunity_score', ascending=False)

    def get_basic_summary(self):
        """
        取得基礎摘要資訊

        Returns:
            dict: 摘要資訊
        """
        return {
            'total_records': len(self.dataset),
            'unique_business_targets': self.dataset['business_name'].nunique(),
            'avg_rating': self.dataset['rating'].mean(),
            'rating_distribution': self.dataset['rating'].value_counts().sort_index().to_dict(),
            'analysis_criteria': {
                'low_rating_threshold': self.low_threshold,
                'high_rating_threshold': self.high_threshold,
                'min_samples_dish': self.min_samples_dish,
                'min_samples_vendor': self.min_samples_vendor
            }
        }

    @abstractmethod
    def analyze(self):
        """
        執行分析（由子類別實作）

        Returns:
            dict: 分析結果
        """
        pass

    @abstractmethod
    def export_results(self, output_dir):
        """
        匯出分析結果（由子類別實作）

        Args:
            output_dir (str): 輸出目錄
        """
        pass