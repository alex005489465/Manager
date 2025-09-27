#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布圖表模組

提供各種分布圖表的生成功能
"""

import matplotlib.pyplot as plt
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from visualization.charts.base_chart import BaseChart

logger = logging.getLogger(__name__)


class DistributionChart(BaseChart):
    """分布圖表生成器"""

    def plot(self, data, title, filename, **kwargs):
        """
        繪製分布直方圖

        Args:
            data: 資料 (可以是DataFrame或Series)
            title (str): 圖表標題
            filename (str): 檔案名稱
            **kwargs: 其他參數
        """
        self.validate_data(data)

        # 設定圖表
        self.setup_figure()

        # 根據資料類型決定繪製方式
        if hasattr(data, 'value_counts') and not hasattr(data, 'columns'):
            # 如果是Series，使用value_counts
            ratings = data.value_counts().sort_index()
        elif hasattr(data, 'columns') and 'rating' in data.columns:
            # 如果是DataFrame且有rating欄位
            ratings = data['rating'].value_counts().sort_index()
        else:
            raise ValueError("資料格式不支援，需要Series或包含'rating'欄位的DataFrame")

        # 創建直方圖
        # 確保 x 軸資料是數值類型
        try:
            x_values = [float(x) for x in ratings.index]
        except (ValueError, TypeError) as e:
            logger.error(f"無法轉換索引為數值: {ratings.index}, 錯誤: {e}")
            # 如果轉換失敗，使用數值範圍
            x_values = list(range(len(ratings.index)))
        bars = plt.bar(
            x_values,
            ratings.values,
            color=kwargs.get('color', 'skyblue'),
            alpha=0.8
        )

        # 設定標籤
        self.add_labels(xlabel='評分 (星)', ylabel='數量')
        self.add_title(title)

        # 在長條上顯示數值
        for bar, value in zip(bars, ratings.values):
            plt.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 1,
                str(value),
                ha='center', va='bottom', fontsize=10
            )

        # 設定 x 軸刻度
        plt.xticks(range(1, 6))
        plt.grid(axis='y', alpha=0.3)

        # 調整布局並儲存
        self.apply_layout()
        return self.save_chart(filename)

    def plot_rating_distribution(self, dataset, title="評分分布", filename="rating_distribution.png"):
        """
        繪製評分分布直方圖

        Args:
            dataset (pd.DataFrame): 核心資料集
            title (str): 圖表標題
            filename (str): 檔案名稱
        """
        return self.plot(dataset, title, filename)