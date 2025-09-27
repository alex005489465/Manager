#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析工作流程模組

負責協調整個商機分析流程的執行
"""

import os
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import ANALYSIS_CONFIG
from data import get_db_connector, DatasetBuilder
from analysis.analyzers import OpportunityAnalyzer
from visualization.renderers import ChartRenderer
from orchestration.reports import ReportGenerator

# 設定日誌
logger = logging.getLogger(__name__)


class AnalysisWorkflow:
    """分析工作流程編排器"""

    def __init__(self):
        """初始化工作流程編排器"""
        self.start_time = datetime.now()
        self.results = {}

        # 確保輸出目錄存在
        for directory in [ANALYSIS_CONFIG['output_dir'], ANALYSIS_CONFIG['charts_dir'],
                         ANALYSIS_CONFIG['reports_dir'], ANALYSIS_CONFIG['data_dir']]:
            os.makedirs(directory, exist_ok=True)

        logger.info("=" * 60)
        logger.info("商機發現分析工具啟動")
        logger.info("=" * 60)

    def test_database_connection(self):
        """測試資料庫連接"""
        logger.info("測試資料庫連接...")
        try:
            db = get_db_connector()
            if db.test_connection():
                logger.info("✓ 資料庫連接成功")
                return True
            else:
                logger.error("✗ 資料庫連接失敗")
                return False
        except Exception as e:
            logger.error(f"✗ 資料庫連接錯誤: {e}")
            return False

    def build_dataset(self):
        """建立核心資料集"""
        logger.info("步驟 1: 建立核心資料集...")
        try:
            builder = DatasetBuilder()
            dataset = builder.build_core_dataset()

            if dataset is None or dataset.empty:
                logger.error("✗ 核心資料集建立失敗或無資料")
                return None

            # 儲存基礎統計
            stats = builder.get_basic_statistics()
            self.results['dataset_stats'] = stats

            # 匯出核心資料集
            builder.export_dataset()

            logger.info(f"✓ 核心資料集建立完成: {len(dataset)} 筆記錄")
            logger.info(f"  - 唯一料理: {stats['unique_dishes']} 種")
            logger.info(f"  - 唯一店家: {stats['unique_vendors']} 家")
            logger.info(f"  - 平均評分: {stats['avg_rating']:.2f} 星")

            return dataset

        except Exception as e:
            logger.error(f"✗ 核心資料集建立失敗: {e}")
            return None

    def analyze_opportunities(self, dataset):
        """進行商機分析"""
        logger.info("步驟 2: 進行商機分析...")
        try:
            analyzer = OpportunityAnalyzer(dataset)

            # 進行統一商機分析
            logger.info("分析統一商機...")
            business_analysis = analyzer.analyze_business_opportunities()

            if business_analysis and 'low_count_opportunities' in business_analysis:
                if not business_analysis['low_count_opportunities'].empty:
                    top_business = business_analysis['low_count_opportunities'].iloc[0]
                    business_type = "料理" if top_business['business_type'] == 'dish' else "店家"
                    logger.info(f"  ✓ 最大商機 ({business_type}): {top_business.name} " +
                              f"({int(top_business['low_rating_count'])} 個低評分, " +
                              f"{top_business['low_rating_ratio']:.1f}% 低評分率)")

            # 為了向後兼容，同時進行分離分析
            dish_analysis = analyzer.analyze_dish_opportunities()
            vendor_analysis = analyzer.analyze_vendor_opportunities()

            # 匯出分析結果
            analyzer.export_results()

            # 生成摘要報告
            summary = analyzer.generate_summary_report(dish_analysis, vendor_analysis)
            self.results['analysis_summary'] = summary
            self.results['business_analysis'] = business_analysis

            logger.info("✓ 商機分析完成")

            return business_analysis, dish_analysis, vendor_analysis

        except Exception as e:
            logger.error(f"✗ 商機分析失敗: {e}")
            return None, None, None

    def generate_visualizations(self, dataset, business_analysis, dish_analysis=None, vendor_analysis=None):
        """生成視覺化圖表"""
        logger.info("步驟 3: 生成視覺化圖表...")
        try:
            renderer = ChartRenderer()
            chart_paths = renderer.generate_all_opportunity_charts(
                business_analysis=business_analysis,
                dish_analysis=dish_analysis,
                vendor_analysis=vendor_analysis,
                dataset=dataset
            )

            logger.info("✓ 視覺化圖表生成完成")
            logger.info(f"  - 圖表儲存位置: {ANALYSIS_CONFIG['charts_dir']}")
            logger.info(f"  - 共生成 {len(chart_paths)} 個圖表")

            return chart_paths

        except Exception as e:
            logger.error(f"✗ 視覺化圖表生成失敗: {e}")
            return []

    def generate_report(self):
        """生成最終摘要報告"""
        logger.info("步驟 4: 生成摘要報告...")
        try:
            end_time = datetime.now()
            execution_time = end_time - self.start_time

            report_generator = ReportGenerator()
            report_path = report_generator.generate_summary_report(
                self.results,
                self.start_time,
                execution_time
            )

            logger.info(f"✓ 摘要報告生成完成: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"✗ 摘要報告生成失敗: {e}")
            return None

    def run_complete_analysis(self):
        """執行完整的商機分析流程"""
        try:
            # 測試資料庫連接
            if not self.test_database_connection():
                logger.error("資料庫連接失敗，無法繼續分析")
                return False

            # 建立核心資料集
            dataset = self.build_dataset()
            if dataset is None:
                logger.error("核心資料集建立失敗，無法繼續分析")
                return False

            # 進行商機分析
            business_analysis, dish_analysis, vendor_analysis = self.analyze_opportunities(dataset)
            if business_analysis is None:
                logger.error("商機分析失敗，無法繼續")
                return False

            # 生成視覺化圖表
            chart_paths = self.generate_visualizations(dataset, business_analysis, dish_analysis, vendor_analysis)

            # 生成摘要報告
            report_path = self.generate_report()

            # 顯示完成訊息
            end_time = datetime.now()
            execution_time = end_time - self.start_time

            logger.info("=" * 60)
            logger.info(">> 商機發現分析完成！")
            logger.info(f">> 總執行時間: {execution_time.total_seconds():.1f} 秒")
            logger.info(f">> 輸出目錄: {ANALYSIS_CONFIG['output_dir']}")
            logger.info(f">> 生成圖表: {len(chart_paths)} 個")
            if report_path:
                logger.info(f">> 摘要報告: {report_path}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"分析流程執行失敗: {e}")
            return False