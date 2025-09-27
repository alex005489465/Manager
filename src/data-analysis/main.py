#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商機發現分析工具 - 主程式

整合所有模組，提供完整的商機分析流程
"""

import os
import sys
import logging
import time
from datetime import datetime

# 導入所有模組
from config import ANALYSIS_CONFIG
from database_connector import get_db_connector
from core_dataset_builder import CoreDatasetBuilder
from opportunity_analyzer import OpportunityAnalyzer
from visualizer import BusinessOpportunityVisualizer

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./output/analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BusinessOpportunityAnalysis:
    """商機發現分析主控制器"""

    def __init__(self):
        """初始化分析控制器"""
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

    def build_core_dataset(self):
        """建立核心資料集"""
        logger.info("步驟 1: 建立核心資料集...")
        try:
            builder = CoreDatasetBuilder()
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

            # 分析料理商機
            logger.info("分析料理商機...")
            dish_analysis = analyzer.analyze_dish_opportunities()

            if dish_analysis and 'low_count_opportunities' in dish_analysis:
                top_dish = dish_analysis['low_count_opportunities'].iloc[0]
                logger.info(f"  ✓ 最大料理商機: {top_dish.name} " +
                          f"({int(top_dish['low_rating_count'])} 個低評分, " +
                          f"{top_dish['low_rating_ratio']:.1f}% 低評分率)")

            # 分析店家商機
            logger.info("分析店家商機...")
            vendor_analysis = analyzer.analyze_vendor_opportunities()

            if vendor_analysis and 'low_count_opportunities' in vendor_analysis:
                top_vendor = vendor_analysis['low_count_opportunities'].iloc[0]
                logger.info(f"  ✓ 最大店家商機: {top_vendor.name} " +
                          f"({int(top_vendor['low_rating_count'])} 個低評分, " +
                          f"{top_vendor['low_rating_ratio']:.1f}% 低評分率)")

            # 匯出分析結果
            analyzer.export_opportunities(dish_analysis, vendor_analysis)

            # 生成摘要報告
            summary = analyzer.generate_summary_report(dish_analysis, vendor_analysis)
            self.results['analysis_summary'] = summary

            logger.info("✓ 商機分析完成")

            return dish_analysis, vendor_analysis

        except Exception as e:
            logger.error(f"✗ 商機分析失敗: {e}")
            return None, None

    def generate_visualizations(self, dataset, dish_analysis, vendor_analysis):
        """生成視覺化圖表"""
        logger.info("步驟 3: 生成視覺化圖表...")
        try:
            visualizer = BusinessOpportunityVisualizer()
            visualizer.generate_all_opportunity_charts(dish_analysis, vendor_analysis, dataset)

            logger.info("✓ 視覺化圖表生成完成")
            logger.info(f"  - 圖表儲存位置: {ANALYSIS_CONFIG['charts_dir']}")

            return True

        except Exception as e:
            logger.error(f"✗ 視覺化圖表生成失敗: {e}")
            return False

    def generate_summary_report(self):
        """生成最終摘要報告"""
        logger.info("步驟 4: 生成摘要報告...")
        try:
            end_time = datetime.now()
            execution_time = end_time - self.start_time

            # 準備報告內容
            report_content = f"""# 商機發現分析報告

## 執行摘要
- **分析時間**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **執行時長**: {execution_time.total_seconds():.1f} 秒
- **分析工具**: Manager 餐廳評論商機發現分析系統

## 資料集概況
"""

            if 'dataset_stats' in self.results:
                stats = self.results['dataset_stats']
                report_content += f"""
- **總食物項目數**: {stats['total_items']} 個
- **唯一料理種類**: {stats['unique_dishes']} 種
- **唯一店家數量**: {stats['unique_vendors']} 家
- **平均評分**: {stats['avg_rating']:.2f} 星

### 評分分布
"""
                for rating, count in stats['rating_distribution'].items():
                    report_content += f"- {rating} 星: {count} 個 ({count/stats['total_items']*100:.1f}%)\n"

            # 添加商機分析結果
            if 'analysis_summary' in self.results:
                summary = self.results['analysis_summary']
                report_content += f"""

## 商機分析結果

### 分析標準
- **低評分門檻**: ≤ {summary['analysis_summary']['analysis_criteria']['low_rating_threshold']} 星
- **高評分門檻**: ≥ {summary['analysis_summary']['analysis_criteria']['high_rating_threshold']} 星
- **料理最少樣本數**: {summary['analysis_summary']['analysis_criteria']['min_samples_dish']} 個
- **店家最少樣本數**: {summary['analysis_summary']['analysis_criteria']['min_samples_vendor']} 個

### 頂級商機發現
"""

                if 'top_dish_opportunity' in summary:
                    dish = summary['top_dish_opportunity']
                    report_content += f"""
#### 🎯 最大料理商機: {dish['name']}
- **低評分數量**: {dish['low_rating_count']} 個 (市場需求大但品質差)
- **低評分比率**: {dish['low_rating_ratio']:.1f}% (評價普遍不佳)
- **總樣本數**: {dish['total_count']} 個
- **平均評分**: {dish['avg_rating']:.2f} 星
- **商機類型**: 市場有需求但現有產品品質不佳，有機會做出優質產品搶占市場
"""

                if 'top_vendor_opportunity' in summary:
                    vendor = summary['top_vendor_opportunity']
                    report_content += f"""
#### 🏪 最大店家商機: {vendor['name']}
- **低評分數量**: {vendor['low_rating_count']} 個 (客流量大但服務差)
- **低評分比率**: {vendor['low_rating_ratio']:.1f}% (評價普遍不佳)
- **總樣本數**: {vendor['total_count']} 個
- **平均評分**: {vendor['avg_rating']:.2f} 星
- **商機類型**: 該店家周邊有市場需求但服務品質差，有機會提供優質替代方案
"""

            # 添加文件說明
            report_content += f"""

## 輸出檔案說明

### 圖表檔案 (`{ANALYSIS_CONFIG['charts_dir']}`)
- `rating_distribution.png`: 整體評分分布圖
- `dish_low_count_opportunities.png`: 料理低評分數量商機榜
- `dish_low_ratio_opportunities.png`: 料理低評分比率商機榜
- `dish_opportunity_matrix.png`: 料理商機矩陣圖
- `vendor_low_count_opportunities.png`: 店家低評分數量商機榜
- `vendor_low_ratio_opportunities.png`: 店家低評分比率商機榜
- `vendor_opportunity_matrix.png`: 店家商機矩陣圖

### 資料檔案 (`{ANALYSIS_CONFIG['data_dir']}`)
- `core_dataset.csv`: 核心分析資料集
- `dish_low_count_opportunities.csv`: 料理低評分數量商機清單
- `dish_low_ratio_opportunities.csv`: 料理低評分比率商機清單
- `vendor_low_count_opportunities.csv`: 店家低評分數量商機清單
- `vendor_low_ratio_opportunities.csv`: 店家低評分比率商機清單

## 建議行動方案

1. **優先關注低評分數量高的項目**: 這些代表市場需求大但品質不佳的領域
2. **研究低評分比率高的項目**: 這些代表評價普遍很差，有改善空間
3. **參考高評分競爭對手**: 了解市場標竿和品質期望
4. **詳細市場調研**: 針對發現的商機進行實地調查和驗證

---
*本報告由 Manager 餐廳評論商機發現分析系統自動生成*
"""

            # 儲存報告
            report_path = os.path.join(ANALYSIS_CONFIG['reports_dir'], 'business_opportunity_report.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            logger.info(f"✓ 摘要報告生成完成: {report_path}")
            return True

        except Exception as e:
            logger.error(f"✗ 摘要報告生成失敗: {e}")
            return False

    def run_complete_analysis(self):
        """執行完整的商機分析流程"""
        try:
            # 測試資料庫連接
            if not self.test_database_connection():
                logger.error("資料庫連接失敗，無法繼續分析")
                return False

            # 建立核心資料集
            dataset = self.build_core_dataset()
            if dataset is None:
                logger.error("核心資料集建立失敗，無法繼續分析")
                return False

            # 進行商機分析
            dish_analysis, vendor_analysis = self.analyze_opportunities(dataset)
            if dish_analysis is None and vendor_analysis is None:
                logger.error("商機分析失敗，無法繼續")
                return False

            # 生成視覺化圖表
            self.generate_visualizations(dataset, dish_analysis, vendor_analysis)

            # 生成摘要報告
            self.generate_summary_report()

            # 顯示完成訊息
            end_time = datetime.now()
            execution_time = end_time - self.start_time

            logger.info("=" * 60)
            logger.info(">> 商機發現分析完成！")
            logger.info(f">> 總執行時間: {execution_time.total_seconds():.1f} 秒")
            logger.info(f">> 輸出目錄: {ANALYSIS_CONFIG['output_dir']}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"分析流程執行失敗: {e}")
            return False


def main():
    """主執行函數"""
    print(">> Manager 餐廳評論商機發現分析工具")
    print("=" * 50)

    try:
        # 初始化分析控制器
        analysis = BusinessOpportunityAnalysis()

        # 執行完整分析
        success = analysis.run_complete_analysis()

        if success:
            print("\n>> 分析完成！請查看 output 目錄中的結果檔案。")
            return 0
        else:
            print("\n>> 分析過程中發生錯誤，請查看日誌了解詳情。")
            return 1

    except KeyboardInterrupt:
        print("\n>> 分析被使用者中斷")
        return 1
    except Exception as e:
        print(f"\n>> 程式執行錯誤: {e}")
        logger.error(f"程式執行錯誤: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())