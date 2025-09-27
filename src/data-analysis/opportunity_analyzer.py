#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商機發現分析模組

專注於找出低評分商機和高評分競爭對手
"""

import pandas as pd
import logging
from config import ANALYSIS_CONFIG
import os

# 設定日誌
logger = logging.getLogger(__name__)


class OpportunityAnalyzer:
    """商機分析器"""

    def __init__(self, core_dataset):
        """
        初始化商機分析器

        Args:
            core_dataset (pd.DataFrame): 核心資料集
        """
        self.dataset = core_dataset
        self.low_threshold = ANALYSIS_CONFIG['low_rating_threshold']
        self.high_threshold = ANALYSIS_CONFIG['high_rating_threshold']
        self.min_samples_dish = ANALYSIS_CONFIG['min_samples_dish']
        self.min_samples_vendor = ANALYSIS_CONFIG['min_samples_vendor']
        self.top_n = ANALYSIS_CONFIG['top_n_items']

    def analyze_business_opportunities(self):
        """
        分析統一商業標的商機（包含料理和店家）

        Returns:
            dict: 包含低評分數量、低評分比率、高評分參考的分析結果
        """
        logger.info("開始分析統一商業標的商機...")

        # 按商業標的分組統計
        business_stats = self.dataset.groupby('business_name').agg({
            'rating': ['count', 'mean', lambda x: (x <= self.low_threshold).sum(),
                      lambda x: (x >= self.high_threshold).sum()],
            'business_type': 'first'  # 取得商業類型
        }).round(2)

        # 重新命名欄位
        business_stats.columns = ['total_count', 'avg_rating', 'low_rating_count', 'high_rating_count', 'business_type']
        business_stats['low_rating_ratio'] = (business_stats['low_rating_count'] / business_stats['total_count'] * 100).round(2)
        business_stats['high_rating_ratio'] = (business_stats['high_rating_count'] / business_stats['total_count'] * 100).round(2)

        # 過濾最少樣本數 (統一使用料理的標準)
        business_stats = business_stats[business_stats['total_count'] >= self.min_samples_dish]

        logger.info(f"符合最少樣本數 ({self.min_samples_dish}) 的商業標的: {len(business_stats)} 個")
        logger.info(f"  - 料理類型: {(business_stats['business_type'] == 'dish').sum()} 個")
        logger.info(f"  - 店家類型: {(business_stats['business_type'] == 'vendor').sum()} 個")

        # 商機分析 - 低評分數量排行榜
        low_count_opportunities = business_stats.sort_values(
            ['low_rating_count', 'low_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 商機分析 - 低評分比率排行榜
        low_ratio_opportunities = business_stats.sort_values(
            ['low_rating_ratio', 'low_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分數量排行榜
        high_count_competitors = business_stats.sort_values(
            ['high_rating_count', 'high_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分比率排行榜
        high_ratio_competitors = business_stats.sort_values(
            ['high_rating_ratio', 'high_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        return {
            'all_stats': business_stats,
            'low_count_opportunities': low_count_opportunities,
            'low_ratio_opportunities': low_ratio_opportunities,
            'high_count_competitors': high_count_competitors,
            'high_ratio_competitors': high_ratio_competitors
        }

    def analyze_dish_opportunities(self):
        """
        分析料理商機 (保留舊方法以維持兼容性)

        Returns:
            dict: 包含低評分數量、低評分比率、高評分參考的分析結果
        """
        logger.info("開始分析料理商機...")

        # 過濾料理類型的資料
        dish_dataset = self.dataset[self.dataset['business_type'] == 'dish']
        if dish_dataset.empty:
            logger.warning("沒有料理類型的資料")
            return {}

        # 按料理分組統計
        dish_stats = dish_dataset.groupby('business_name').agg({
            'rating': ['count', 'mean', lambda x: (x <= self.low_threshold).sum(),
                      lambda x: (x >= self.high_threshold).sum()]
        }).round(2)

        # 重新命名欄位
        dish_stats.columns = ['total_count', 'avg_rating', 'low_rating_count', 'high_rating_count']
        dish_stats['low_rating_ratio'] = (dish_stats['low_rating_count'] / dish_stats['total_count'] * 100).round(2)
        dish_stats['high_rating_ratio'] = (dish_stats['high_rating_count'] / dish_stats['total_count'] * 100).round(2)

        # 過濾最少樣本數
        dish_stats = dish_stats[dish_stats['total_count'] >= self.min_samples_dish]

        logger.info(f"符合最少樣本數 ({self.min_samples_dish}) 的料理: {len(dish_stats)} 種")

        # 商機分析 - 低評分數量排行榜
        low_count_opportunities = dish_stats.sort_values(
            ['low_rating_count', 'low_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 商機分析 - 低評分比率排行榜
        low_ratio_opportunities = dish_stats.sort_values(
            ['low_rating_ratio', 'low_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分數量排行榜
        high_count_competitors = dish_stats.sort_values(
            ['high_rating_count', 'high_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分比率排行榜
        high_ratio_competitors = dish_stats.sort_values(
            ['high_rating_ratio', 'high_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        return {
            'all_stats': dish_stats,
            'low_count_opportunities': low_count_opportunities,
            'low_ratio_opportunities': low_ratio_opportunities,
            'high_count_competitors': high_count_competitors,
            'high_ratio_competitors': high_ratio_competitors
        }

    def analyze_vendor_opportunities(self):
        """
        分析店家商機 (保留舊方法以維持兼容性)

        Returns:
            dict: 包含低評分數量、低評分比率、高評分參考的分析結果
        """
        logger.info("開始分析店家商機...")

        # 過濾店家類型的資料
        vendor_dataset = self.dataset[self.dataset['business_type'] == 'vendor']

        if vendor_dataset.empty:
            logger.warning("沒有店家類型的資料")
            return {}

        # 按店家分組統計
        vendor_stats = vendor_dataset.groupby('business_name').agg({
            'rating': ['count', 'mean', lambda x: (x <= self.low_threshold).sum(),
                      lambda x: (x >= self.high_threshold).sum()]
        }).round(2)

        # 重新命名欄位
        vendor_stats.columns = ['total_count', 'avg_rating', 'low_rating_count', 'high_rating_count']
        vendor_stats['low_rating_ratio'] = (vendor_stats['low_rating_count'] / vendor_stats['total_count'] * 100).round(2)
        vendor_stats['high_rating_ratio'] = (vendor_stats['high_rating_count'] / vendor_stats['total_count'] * 100).round(2)

        # 過濾最少樣本數
        vendor_stats = vendor_stats[vendor_stats['total_count'] >= self.min_samples_vendor]

        logger.info(f"符合最少樣本數 ({self.min_samples_vendor}) 的店家: {len(vendor_stats)} 家")

        # 商機分析 - 低評分數量排行榜
        low_count_opportunities = vendor_stats.sort_values(
            ['low_rating_count', 'low_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 商機分析 - 低評分比率排行榜
        low_ratio_opportunities = vendor_stats.sort_values(
            ['low_rating_ratio', 'low_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分數量排行榜
        high_count_competitors = vendor_stats.sort_values(
            ['high_rating_count', 'high_rating_ratio'],
            ascending=[False, False]
        ).head(self.top_n)

        # 競爭對手參考 - 高評分比率排行榜
        high_ratio_competitors = vendor_stats.sort_values(
            ['high_rating_ratio', 'high_rating_count'],
            ascending=[False, False]
        ).head(self.top_n)

        return {
            'all_stats': vendor_stats,
            'low_count_opportunities': low_count_opportunities,
            'low_ratio_opportunities': low_ratio_opportunities,
            'high_count_competitors': high_count_competitors,
            'high_ratio_competitors': high_ratio_competitors
        }

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

    def export_opportunities(self, dish_analysis, vendor_analysis):
        """
        匯出商機分析結果

        Args:
            dish_analysis (dict): 料理分析結果
            vendor_analysis (dict): 店家分析結果
        """
        output_dir = ANALYSIS_CONFIG['data_dir']
        os.makedirs(output_dir, exist_ok=True)

        # 匯出料理商機
        if dish_analysis:
            # 低評分數量商機
            dish_analysis['low_count_opportunities'].to_csv(
                os.path.join(output_dir, 'dish_low_count_opportunities.csv'),
                encoding='utf-8-sig'
            )

            # 低評分比率商機
            dish_analysis['low_ratio_opportunities'].to_csv(
                os.path.join(output_dir, 'dish_low_ratio_opportunities.csv'),
                encoding='utf-8-sig'
            )

            # 高評分競爭對手參考
            dish_analysis['high_count_competitors'].to_csv(
                os.path.join(output_dir, 'dish_high_count_competitors.csv'),
                encoding='utf-8-sig'
            )

            logger.info("料理商機分析結果已匯出")

        # 匯出店家商機
        if vendor_analysis:
            # 低評分數量商機
            vendor_analysis['low_count_opportunities'].to_csv(
                os.path.join(output_dir, 'vendor_low_count_opportunities.csv'),
                encoding='utf-8-sig'
            )

            # 低評分比率商機
            vendor_analysis['low_ratio_opportunities'].to_csv(
                os.path.join(output_dir, 'vendor_low_ratio_opportunities.csv'),
                encoding='utf-8-sig'
            )

            # 高評分競爭對手參考
            vendor_analysis['high_count_competitors'].to_csv(
                os.path.join(output_dir, 'vendor_high_count_competitors.csv'),
                encoding='utf-8-sig'
            )

            logger.info("店家商機分析結果已匯出")

    def generate_summary_report(self, dish_analysis, vendor_analysis):
        """
        生成商機摘要報告

        Args:
            dish_analysis (dict): 料理分析結果
            vendor_analysis (dict): 店家分析結果

        Returns:
            dict: 摘要報告
        """
        summary = {
            'analysis_summary': {
                'total_dishes_analyzed': len(dish_analysis.get('all_stats', [])) if dish_analysis else 0,
                'total_vendors_analyzed': len(vendor_analysis.get('all_stats', [])) if vendor_analysis else 0,
                'analysis_criteria': {
                    'low_rating_threshold': self.low_threshold,
                    'high_rating_threshold': self.high_threshold,
                    'min_samples_dish': self.min_samples_dish,
                    'min_samples_vendor': self.min_samples_vendor
                }
            }
        }

        # 料理商機摘要
        if dish_analysis and 'low_count_opportunities' in dish_analysis and not dish_analysis['low_count_opportunities'].empty:
            top_dish_opportunity = dish_analysis['low_count_opportunities'].iloc[0]
            summary['top_dish_opportunity'] = {
                'name': top_dish_opportunity.name,
                'low_rating_count': int(top_dish_opportunity['low_rating_count']),
                'low_rating_ratio': float(top_dish_opportunity['low_rating_ratio']),
                'total_count': int(top_dish_opportunity['total_count']),
                'avg_rating': float(top_dish_opportunity['avg_rating'])
            }

        # 店家商機摘要
        if vendor_analysis and 'low_count_opportunities' in vendor_analysis and not vendor_analysis['low_count_opportunities'].empty:
            top_vendor_opportunity = vendor_analysis['low_count_opportunities'].iloc[0]
            summary['top_vendor_opportunity'] = {
                'name': top_vendor_opportunity.name,
                'low_rating_count': int(top_vendor_opportunity['low_rating_count']),
                'low_rating_ratio': float(top_vendor_opportunity['low_rating_ratio']),
                'total_count': int(top_vendor_opportunity['total_count']),
                'avg_rating': float(top_vendor_opportunity['avg_rating'])
            }

        return summary


if __name__ == "__main__":
    # 測試商機分析
    print("測試商機分析...")

    # 模擬核心資料集（實際使用時從 core_dataset_builder 取得）
    from core_dataset_builder import CoreDatasetBuilder

    try:
        # 建立核心資料集
        builder = CoreDatasetBuilder()
        dataset = builder.build_core_dataset()

        # 初始化商機分析器
        analyzer = OpportunityAnalyzer(dataset)

        # 分析料理商機
        dish_analysis = analyzer.analyze_dish_opportunities()
        print(f">> 料理商機分析完成")
        print(f"   低評分數量 TOP1: {dish_analysis['low_count_opportunities'].index[0]} " +
              f"({dish_analysis['low_count_opportunities'].iloc[0]['low_rating_count']} 個低評分)")

        # 分析店家商機
        vendor_analysis = analyzer.analyze_vendor_opportunities()
        if vendor_analysis:
            print(f">> 店家商機分析完成")
            print(f"   低評分數量 TOP1: {vendor_analysis['low_count_opportunities'].index[0]} " +
                  f"({vendor_analysis['low_count_opportunities'].iloc[0]['low_rating_count']} 個低評分)")

        # 匯出結果
        analyzer.export_opportunities(dish_analysis, vendor_analysis)
        print(">> 商機分析結果已匯出")

        # 生成摘要報告
        summary = analyzer.generate_summary_report(dish_analysis, vendor_analysis)
        print(f">> 分析了 {summary['analysis_summary']['total_dishes_analyzed']} 種料理")
        print(f">> 分析了 {summary['analysis_summary']['total_vendors_analyzed']} 家店家")

    except Exception as e:
        print(f">> 商機分析測試失敗: {e}")
        logger.error(f"測試失敗: {e}", exc_info=True)