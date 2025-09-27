#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
視覺化模組

產生商機分析相關圖表
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import os
import logging
from config import ANALYSIS_CONFIG, CHART_CONFIG

# 設定中文字體和日誌
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
logger = logging.getLogger(__name__)


class BusinessOpportunityVisualizer:
    """商機視覺化器"""

    def __init__(self):
        """初始化視覺化器"""
        self.output_dir = ANALYSIS_CONFIG['charts_dir']
        os.makedirs(self.output_dir, exist_ok=True)

        # 設定圖表樣式
        plt.style.use('default')  # 改用 default 樣式避免 seaborn 版本問題
        sns.set_palette(CHART_CONFIG['color_palette'])

    def plot_opportunity_ranking(self, data, title, filename, ranking_type='count'):
        """
        繪製商機排行榜

        Args:
            data (pd.DataFrame): 排行榜資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            ranking_type (str): 排行類型 ('count' 或 'ratio')
        """
        if data.empty:
            logger.warning(f"無資料可繪製: {title}")
            return

        # 準備資料
        if ranking_type == 'count':
            y_values = data['low_rating_count']
            y_label = '低評分數量'
        else:
            y_values = data['low_rating_ratio']
            y_label = '低評分比率 (%)'

        # 設定圖表大小
        plt.figure(figsize=CHART_CONFIG['figure_size'])

        # 創建橫向長條圖
        bars = plt.barh(range(len(data)), y_values, color='lightcoral', alpha=0.8)

        # 設定標籤
        plt.yticks(range(len(data)), data.index, fontsize=10)
        plt.xlabel(y_label, fontsize=CHART_CONFIG['font_size'])
        plt.title(title, fontsize=CHART_CONFIG['title_size'], fontweight='bold')

        # 在長條上顯示數值
        for i, (bar, value) in enumerate(zip(bars, y_values)):
            plt.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}', ha='left', va='center', fontsize=9)

        # 調整布局
        plt.tight_layout()

        # 儲存圖表
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"圖表已儲存: {output_path}")

    def plot_competitor_ranking(self, data, title, filename, ranking_type='count'):
        """
        繪製競爭對手排行榜

        Args:
            data (pd.DataFrame): 排行榜資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            ranking_type (str): 排行類型 ('count' 或 'ratio')
        """
        if data.empty:
            logger.warning(f"無資料可繪製: {title}")
            return

        # 準備資料
        if ranking_type == 'count':
            y_values = data['high_rating_count']
            y_label = '高評分數量'
        else:
            y_values = data['high_rating_ratio']
            y_label = '高評分比率 (%)'

        # 設定圖表大小
        plt.figure(figsize=CHART_CONFIG['figure_size'])

        # 創建橫向長條圖
        bars = plt.barh(range(len(data)), y_values, color='lightgreen', alpha=0.8)

        # 設定標籤
        plt.yticks(range(len(data)), data.index, fontsize=10)
        plt.xlabel(y_label, fontsize=CHART_CONFIG['font_size'])
        plt.title(title, fontsize=CHART_CONFIG['title_size'], fontweight='bold')

        # 在長條上顯示數值
        for i, (bar, value) in enumerate(zip(bars, y_values)):
            plt.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}', ha='left', va='center', fontsize=9)

        # 調整布局
        plt.tight_layout()

        # 儲存圖表
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"圖表已儲存: {output_path}")

    def plot_opportunity_matrix(self, data, title, filename, item_type='料理'):
        """
        繪製商機矩陣圖 (低評分數量 vs 低評分比率)

        Args:
            data (pd.DataFrame): 分析資料
            title (str): 圖表標題
            filename (str): 檔案名稱
            item_type (str): 項目類型
        """
        if data.empty:
            logger.warning(f"無資料可繪製: {title}")
            return

        # 設定圖表大小
        plt.figure(figsize=CHART_CONFIG['figure_size'])

        # 創建散布圖
        scatter = plt.scatter(data['low_rating_count'], data['low_rating_ratio'],
                            s=data['total_count']*10, alpha=0.6, c='red')

        # 設定標籤
        plt.xlabel('低評分數量', fontsize=CHART_CONFIG['font_size'])
        plt.ylabel('低評分比率 (%)', fontsize=CHART_CONFIG['font_size'])
        plt.title(title, fontsize=CHART_CONFIG['title_size'], fontweight='bold')

        # 添加象限分割線
        median_count = data['low_rating_count'].median()
        median_ratio = data['low_rating_ratio'].median()
        plt.axvline(x=median_count, color='gray', linestyle='--', alpha=0.5)
        plt.axhline(y=median_ratio, color='gray', linestyle='--', alpha=0.5)

        # 添加象限標籤
        max_count = data['low_rating_count'].max()
        max_ratio = data['low_rating_ratio'].max()
        plt.text(max_count*0.75, max_ratio*0.9, '高數量\n高比率\n(最佳商機)',
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        # 標註前5名
        top_5 = data.head(5)
        for idx, row in top_5.iterrows():
            plt.annotate(idx, (row['low_rating_count'], row['low_rating_ratio']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

        # 添加圖例
        plt.legend([f'{item_type}樣本數'], loc='upper left')

        # 調整布局
        plt.tight_layout()

        # 儲存圖表
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"圖表已儲存: {output_path}")

    def plot_rating_distribution(self, dataset, title="評分分布", filename="rating_distribution.png"):
        """
        繪製評分分布直方圖

        Args:
            dataset (pd.DataFrame): 核心資料集
            title (str): 圖表標題
            filename (str): 檔案名稱
        """
        # 設定圖表大小
        plt.figure(figsize=CHART_CONFIG['figure_size'])

        # 創建直方圖
        ratings = dataset['rating'].value_counts().sort_index()
        bars = plt.bar(ratings.index, ratings.values, color='skyblue', alpha=0.8)

        # 設定標籤
        plt.xlabel('評分 (星)', fontsize=CHART_CONFIG['font_size'])
        plt.ylabel('數量', fontsize=CHART_CONFIG['font_size'])
        plt.title(title, fontsize=CHART_CONFIG['title_size'], fontweight='bold')

        # 在長條上顯示數值
        for bar, value in zip(bars, ratings.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(value), ha='center', va='bottom', fontsize=10)

        # 設定 x 軸刻度
        plt.xticks(range(1, 6))
        plt.grid(axis='y', alpha=0.3)

        # 調整布局
        plt.tight_layout()

        # 儲存圖表
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
        plt.close()

        logger.info(f"圖表已儲存: {output_path}")

    def generate_all_opportunity_charts(self, business_analysis=None, dish_analysis=None, vendor_analysis=None, dataset=None):
        """
        生成所有商機分析圖表

        Args:
            business_analysis (dict): 統一商機分析結果 (新)
            dish_analysis (dict): 料理分析結果 (向後兼容)
            vendor_analysis (dict): 店家分析結果 (向後兼容)
            dataset (pd.DataFrame): 核心資料集
        """
        logger.info("開始生成商機分析圖表...")

        # 評分分布圖
        if dataset is not None:
            self.plot_rating_distribution(dataset)

        # 優先使用統一商機分析
        if business_analysis:
            self._generate_business_charts(business_analysis)

        # 向後兼容：如果沒有統一分析結果，使用分離的分析結果
        elif dish_analysis or vendor_analysis:
            self._generate_legacy_charts(dish_analysis, vendor_analysis)

    def _generate_business_charts(self, business_analysis):
        """生成統一商機分析圖表"""
        logger.info("生成統一商機分析圖表...")

        # 統一商機排行榜 - 低評分數量
        self.plot_opportunity_ranking(
            business_analysis['low_count_opportunities'],
            '商機排行榜 - 低評分數量 (市場需求大但品質差)',
            'business_low_count_opportunities.png',
            'count'
        )

        # 統一商機排行榜 - 低評分比率
        self.plot_opportunity_ranking(
            business_analysis['low_ratio_opportunities'],
            '商機排行榜 - 低評分比率 (評價普遍很差)',
            'business_low_ratio_opportunities.png',
            'ratio'
        )

        # 競爭對手參考 - 高評分數量
        self.plot_competitor_ranking(
            business_analysis['high_count_competitors'],
            '競爭對手參考 - 高評分數量',
            'business_high_count_competitors.png',
            'count'
        )

        # 商機矩陣圖
        self.plot_opportunity_matrix(
            business_analysis['all_stats'],
            '商機矩陣圖 (低評分數量 vs 比率)',
            'business_opportunity_matrix.png',
            '商業標的'
        )

        # 按類型分別生成圖表
        all_stats = business_analysis['all_stats']
        dish_stats = all_stats[all_stats['business_type'] == 'dish']
        vendor_stats = all_stats[all_stats['business_type'] == 'vendor']

        if not dish_stats.empty:
            self.plot_opportunity_ranking(
                dish_stats.sort_values(['low_rating_count', 'low_rating_ratio'], ascending=[False, False]).head(10),
                '料理商機排行榜 - 低評分數量',
                'dish_low_count_opportunities.png',
                'count'
            )

        if not vendor_stats.empty:
            self.plot_opportunity_ranking(
                vendor_stats.sort_values(['low_rating_count', 'low_rating_ratio'], ascending=[False, False]).head(10),
                '店家商機排行榜 - 低評分數量',
                'vendor_low_count_opportunities.png',
                'count'
            )

    def _generate_legacy_charts(self, dish_analysis, vendor_analysis):
        """生成分離的商機分析圖表 (向後兼容)"""
        logger.info("生成分離式商機分析圖表...")

        # 料理商機圖表
        if dish_analysis:
            # 低評分數量排行榜
            self.plot_opportunity_ranking(
                dish_analysis['low_count_opportunities'],
                '料理商機排行榜 - 低評分數量 (市場需求大但品質差)',
                'dish_low_count_opportunities.png',
                'count'
            )

            # 低評分比率排行榜
            self.plot_opportunity_ranking(
                dish_analysis['low_ratio_opportunities'],
                '料理商機排行榜 - 低評分比率 (評價普遍很差)',
                'dish_low_ratio_opportunities.png',
                'ratio'
            )

            # 高評分競爭對手參考
            self.plot_competitor_ranking(
                dish_analysis['high_count_competitors'],
                '料理競爭對手參考 - 高評分數量',
                'dish_high_count_competitors.png',
                'count'
            )

            # 商機矩陣圖
            self.plot_opportunity_matrix(
                dish_analysis['all_stats'],
                '料理商機矩陣圖 (低評分數量 vs 比率)',
                'dish_opportunity_matrix.png',
                '料理'
            )

        # 店家商機圖表
        if vendor_analysis:
            # 低評分數量排行榜
            self.plot_opportunity_ranking(
                vendor_analysis['low_count_opportunities'],
                '店家商機排行榜 - 低評分數量 (客流量大但服務差)',
                'vendor_low_count_opportunities.png',
                'count'
            )

            # 低評分比率排行榜
            self.plot_opportunity_ranking(
                vendor_analysis['low_ratio_opportunities'],
                '店家商機排行榜 - 低評分比率 (評價普遍很差)',
                'vendor_low_ratio_opportunities.png',
                'ratio'
            )

            # 高評分競爭對手參考
            self.plot_competitor_ranking(
                vendor_analysis['high_count_competitors'],
                '店家競爭對手參考 - 高評分數量',
                'vendor_high_count_competitors.png',
                'count'
            )

            # 商機矩陣圖
            self.plot_opportunity_matrix(
                vendor_analysis['all_stats'],
                '店家商機矩陣圖 (低評分數量 vs 比率)',
                'vendor_opportunity_matrix.png',
                '店家'
            )

        logger.info("所有商機分析圖表生成完成")


if __name__ == "__main__":
    # 測試視覺化功能
    print("測試視覺化功能...")

    try:
        from core_dataset_builder import CoreDatasetBuilder
        from opportunity_analyzer import OpportunityAnalyzer

        # 建立核心資料集
        builder = CoreDatasetBuilder()
        dataset = builder.build_core_dataset()

        # 進行商機分析
        analyzer = OpportunityAnalyzer(dataset)
        dish_analysis = analyzer.analyze_dish_opportunities()
        vendor_analysis = analyzer.analyze_vendor_opportunities()

        # 初始化視覺化器
        visualizer = BusinessOpportunityVisualizer()

        # 生成所有圖表
        visualizer.generate_all_opportunity_charts(dish_analysis, vendor_analysis, dataset)

        print(">> 視覺化測試完成，圖表已儲存至 output/charts/ 目錄")

    except Exception as e:
        print(f">> 視覺化測試失敗: {e}")
        logger.error(f"測試失敗: {e}", exc_info=True)