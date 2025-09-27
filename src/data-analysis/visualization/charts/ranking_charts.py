#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排行榜圖表模組

提供各種排行榜圖表的生成功能
"""

import matplotlib.pyplot as plt
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from visualization.charts.base_chart import BaseChart

logger = logging.getLogger(__name__)


class RankingChart(BaseChart):
    """排行榜圖表生成器"""

    def plot(self, data, title, filename, ranking_type='count', **kwargs):
        """
        繪製排行榜圖表

        Args:
            data (pd.DataFrame): 排行榜資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            ranking_type (str): 排行類型 ('count' 或 'ratio')
            **kwargs: 其他參數
        """
        self.validate_data(data)

        # 準備資料
        if ranking_type == 'count':
            y_values = data['low_rating_count']
            y_label = '低評分數量'
            color = kwargs.get('color', 'lightcoral')
        else:
            y_values = data['low_rating_ratio']
            y_label = '低評分比率 (%)'
            color = kwargs.get('color', 'lightcoral')

        # 設定圖表
        self.setup_figure()

        # 創建橫向長條圖
        bars = plt.barh(range(len(data)), y_values, color=color, alpha=0.8)

        # 設定標籤
        plt.yticks(range(len(data)), data.index, fontsize=10)
        self.add_labels(xlabel=y_label)
        self.add_title(title)

        # 在長條上顯示數值
        self.add_value_labels(bars, y_values)

        # 調整布局並儲存
        self.apply_layout()
        return self.save_chart(filename)

    def plot_opportunity_ranking(self, data, title, filename, ranking_type='count'):
        """
        繪製商機排行榜

        Args:
            data (pd.DataFrame): 排行榜資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            ranking_type (str): 排行類型 ('count' 或 'ratio')
        """
        return self.plot(data, title, filename, ranking_type, color='lightcoral')

    def plot_competitor_ranking(self, data, title, filename, ranking_type='count'):
        """
        繪製競爭對手排行榜

        Args:
            data (pd.DataFrame): 排行榜資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            ranking_type (str): 排行類型 ('count' 或 'ratio')
        """
        if self.validate_data(data):
            logger.warning(f"無資料可繪製: {title}")
            return None

        # 準備資料
        if ranking_type == 'count':
            y_values = data['high_rating_count']
            y_label = '高評分數量'
        else:
            y_values = data['high_rating_ratio']
            y_label = '高評分比率 (%)'

        # 設定圖表
        self.setup_figure()

        # 創建橫向長條圖
        bars = plt.barh(range(len(data)), y_values, color='lightgreen', alpha=0.8)

        # 設定標籤
        plt.yticks(range(len(data)), data.index, fontsize=10)
        self.add_labels(xlabel=y_label)
        self.add_title(title)

        # 在長條上顯示數值
        self.add_value_labels(bars, y_values)

        # 調整布局並儲存
        self.apply_layout()
        return self.save_chart(filename)