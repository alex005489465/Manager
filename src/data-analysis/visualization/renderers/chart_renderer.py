#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圖表渲染器模組

統一管理所有圖表的生成和渲染
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from visualization.charts.ranking_charts import RankingChart
from visualization.charts.matrix_charts import MatrixChart
from visualization.charts.distribution_charts import DistributionChart

logger = logging.getLogger(__name__)


class ChartRenderer:
    """圖表渲染器"""

    def __init__(self, output_dir=None):
        """
        初始化圖表渲染器

        Args:
            output_dir (str): 輸出目錄
        """
        self.output_dir = output_dir
        self.ranking_chart = RankingChart(output_dir)
        self.matrix_chart = MatrixChart(output_dir)
        self.distribution_chart = DistributionChart(output_dir)

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

        chart_paths = []

        # 評分分布圖
        if dataset is not None:
            path = self.distribution_chart.plot_rating_distribution(dataset)
            chart_paths.append(path)

        # 優先使用統一商機分析
        if business_analysis:
            paths = self._generate_business_charts(business_analysis)
            chart_paths.extend(paths)

        # 向後兼容：如果沒有統一分析結果，使用分離的分析結果
        elif dish_analysis or vendor_analysis:
            paths = self._generate_legacy_charts(dish_analysis, vendor_analysis)
            chart_paths.extend(paths)

        logger.info(f"所有商機分析圖表生成完成，共生成 {len(chart_paths)} 個圖表")
        return chart_paths

    def _generate_business_charts(self, business_analysis):
        """生成統一商機分析圖表"""
        logger.info("生成統一商機分析圖表...")
        chart_paths = []

        # 統一商機排行榜 - 低評分數量
        if not business_analysis['low_count_opportunities'].empty:
            path = self.ranking_chart.plot_opportunity_ranking(
                business_analysis['low_count_opportunities'],
                '商機排行榜 - 低評分數量 (市場需求大但品質差)',
                'business_low_count_opportunities.png',
                'count'
            )
            chart_paths.append(path)

        # 統一商機排行榜 - 低評分比率
        if not business_analysis['low_ratio_opportunities'].empty:
            path = self.ranking_chart.plot_opportunity_ranking(
                business_analysis['low_ratio_opportunities'],
                '商機排行榜 - 低評分比率 (評價普遍很差)',
                'business_low_ratio_opportunities.png',
                'ratio'
            )
            chart_paths.append(path)

        # 競爭對手參考 - 高評分數量
        if not business_analysis['high_count_competitors'].empty:
            path = self.ranking_chart.plot_competitor_ranking(
                business_analysis['high_count_competitors'],
                '競爭對手參考 - 高評分數量',
                'business_high_count_competitors.png',
                'count'
            )
            chart_paths.append(path)

        # 商機矩陣圖
        if not business_analysis['all_stats'].empty:
            path = self.matrix_chart.plot_opportunity_matrix(
                business_analysis['all_stats'],
                '商機矩陣圖 (低評分數量 vs 比率)',
                'business_opportunity_matrix.png',
                '商業標的'
            )
            chart_paths.append(path)

        # 按類型分別生成圖表
        all_stats = business_analysis['all_stats']
        dish_stats = all_stats[all_stats['business_type'] == 'dish']
        vendor_stats = all_stats[all_stats['business_type'] == 'vendor']

        if not dish_stats.empty:
            path = self.ranking_chart.plot_opportunity_ranking(
                dish_stats.sort_values(['low_rating_count', 'low_rating_ratio'], ascending=[False, False]).head(10),
                '料理商機排行榜 - 低評分數量',
                'dish_low_count_opportunities.png',
                'count'
            )
            chart_paths.append(path)

        if not vendor_stats.empty:
            path = self.ranking_chart.plot_opportunity_ranking(
                vendor_stats.sort_values(['low_rating_count', 'low_rating_ratio'], ascending=[False, False]).head(10),
                '店家商機排行榜 - 低評分數量',
                'vendor_low_count_opportunities.png',
                'count'
            )
            chart_paths.append(path)

        return chart_paths

    def _generate_legacy_charts(self, dish_analysis, vendor_analysis):
        """生成分離的商機分析圖表 (向後兼容)"""
        logger.info("生成分離式商機分析圖表...")
        chart_paths = []

        # 料理商機圖表
        if dish_analysis:
            # 低評分數量排行榜
            if not dish_analysis['low_count_opportunities'].empty:
                path = self.ranking_chart.plot_opportunity_ranking(
                    dish_analysis['low_count_opportunities'],
                    '料理商機排行榜 - 低評分數量 (市場需求大但品質差)',
                    'dish_low_count_opportunities.png',
                    'count'
                )
                chart_paths.append(path)

            # 低評分比率排行榜
            if not dish_analysis['low_ratio_opportunities'].empty:
                path = self.ranking_chart.plot_opportunity_ranking(
                    dish_analysis['low_ratio_opportunities'],
                    '料理商機排行榜 - 低評分比率 (評價普遍很差)',
                    'dish_low_ratio_opportunities.png',
                    'ratio'
                )
                chart_paths.append(path)

            # 高評分競爭對手參考
            if not dish_analysis['high_count_competitors'].empty:
                path = self.ranking_chart.plot_competitor_ranking(
                    dish_analysis['high_count_competitors'],
                    '料理競爭對手參考 - 高評分數量',
                    'dish_high_count_competitors.png',
                    'count'
                )
                chart_paths.append(path)

            # 商機矩陣圖
            if not dish_analysis['all_stats'].empty:
                path = self.matrix_chart.plot_opportunity_matrix(
                    dish_analysis['all_stats'],
                    '料理商機矩陣圖 (低評分數量 vs 比率)',
                    'dish_opportunity_matrix.png',
                    '料理'
                )
                chart_paths.append(path)

        # 店家商機圖表
        if vendor_analysis:
            # 低評分數量排行榜
            if not vendor_analysis['low_count_opportunities'].empty:
                path = self.ranking_chart.plot_opportunity_ranking(
                    vendor_analysis['low_count_opportunities'],
                    '店家商機排行榜 - 低評分數量 (客流量大但服務差)',
                    'vendor_low_count_opportunities.png',
                    'count'
                )
                chart_paths.append(path)

            # 低評分比率排行榜
            if not vendor_analysis['low_ratio_opportunities'].empty:
                path = self.ranking_chart.plot_opportunity_ranking(
                    vendor_analysis['low_ratio_opportunities'],
                    '店家商機排行榜 - 低評分比率 (評價普遍很差)',
                    'vendor_low_ratio_opportunities.png',
                    'ratio'
                )
                chart_paths.append(path)

            # 高評分競爭對手參考
            if not vendor_analysis['high_count_competitors'].empty:
                path = self.ranking_chart.plot_competitor_ranking(
                    vendor_analysis['high_count_competitors'],
                    '店家競爭對手參考 - 高評分數量',
                    'vendor_high_count_competitors.png',
                    'count'
                )
                chart_paths.append(path)

            # 商機矩陣圖
            if not vendor_analysis['all_stats'].empty:
                path = self.matrix_chart.plot_opportunity_matrix(
                    vendor_analysis['all_stats'],
                    '店家商機矩陣圖 (低評分數量 vs 比率)',
                    'vendor_opportunity_matrix.png',
                    '店家'
                )
                chart_paths.append(path)

        return chart_paths


# 向後兼容性別名
BusinessOpportunityVisualizer = ChartRenderer