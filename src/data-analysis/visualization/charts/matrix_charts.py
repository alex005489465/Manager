#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矩陣圖表模組

提供散布圖和矩陣圖表的生成功能
"""

import matplotlib.pyplot as plt
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from visualization.charts.base_chart import BaseChart

logger = logging.getLogger(__name__)


class MatrixChart(BaseChart):
    """矩陣圖表生成器"""

    def plot(self, data, title, filename, item_type='項目', **kwargs):
        """
        繪製商機矩陣圖 (低評分數量 vs 低評分比率)

        Args:
            data (pd.DataFrame): 分析資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            item_type (str): 項目類型
            **kwargs: 其他參數
        """
        self.validate_data(data)

        # 設定圖表
        self.setup_figure()

        # 創建散布圖
        scatter = plt.scatter(
            data['low_rating_count'],
            data['low_rating_ratio'],
            s=data['total_count'] * 10,
            alpha=0.6,
            c=kwargs.get('color', 'red')
        )

        # 設定標籤
        self.add_labels(xlabel='低評分數量', ylabel='低評分比率 (%)')
        self.add_title(title)

        # 添加象限分割線
        median_count = data['low_rating_count'].median()
        median_ratio = data['low_rating_ratio'].median()
        plt.axvline(x=median_count, color='gray', linestyle='--', alpha=0.5)
        plt.axhline(y=median_ratio, color='gray', linestyle='--', alpha=0.5)

        # 添加象限標籤
        max_count = data['low_rating_count'].max()
        max_ratio = data['low_rating_ratio'].max()
        plt.text(
            max_count * 0.75, max_ratio * 0.9,
            '高數量\n高比率\n(最佳商機)',
            ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7)
        )

        # 標註前5名
        top_5 = data.head(5)
        for idx, row in top_5.iterrows():
            plt.annotate(
                idx,
                (row['low_rating_count'], row['low_rating_ratio']),
                xytext=(5, 5), textcoords='offset points', fontsize=8,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8)
            )

        # 添加圖例
        plt.legend([f'{item_type}樣本數'], loc='upper left')

        # 調整布局並儲存
        self.apply_layout()
        return self.save_chart(filename)

    def plot_opportunity_matrix(self, data, title, filename, item_type='料理'):
        """
        繪製商機矩陣圖

        Args:
            data (pd.DataFrame): 分析資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            item_type (str): 項目類型
        """
        return self.plot(data, title, filename, item_type)