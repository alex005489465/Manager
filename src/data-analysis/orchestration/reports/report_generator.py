#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
報告生成器模組

負責生成各種分析報告
"""

import os
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import ANALYSIS_CONFIG

# 設定日誌
logger = logging.getLogger(__name__)


class ReportGenerator:
    """報告生成器"""

    def __init__(self, output_dir=None):
        """
        初始化報告生成器

        Args:
            output_dir (str): 輸出目錄，預設使用配置中的目錄
        """
        self.output_dir = output_dir or ANALYSIS_CONFIG['reports_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_summary_report(self, results, start_time, execution_time):
        """
        生成摘要報告

        Args:
            results (dict): 分析結果
            start_time (datetime): 開始時間
            execution_time (timedelta): 執行時間

        Returns:
            str: 報告檔案路徑
        """
        logger.info("生成摘要報告...")

        # 準備報告內容
        report_content = f"""# 商機發現分析報告

## 執行摘要
- **分析時間**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **執行時長**: {execution_time.total_seconds():.1f} 秒
- **分析工具**: Manager 餐廳評論商機發現分析系統

## 資料集概況
"""

        if 'dataset_stats' in results:
            stats = results['dataset_stats']
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
        if 'analysis_summary' in results:
            summary = results['analysis_summary']
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

        # 添加統一商機分析摘要
        if 'business_analysis' in results:
            business_analysis = results['business_analysis']
            if business_analysis and 'low_count_opportunities' in business_analysis:
                if not business_analysis['low_count_opportunities'].empty:
                    top_business = business_analysis['low_count_opportunities'].iloc[0]
                    business_type_name = "料理" if top_business['business_type'] == 'dish' else "店家"
                    report_content += f"""

### 🚀 統一商機分析最佳發現
#### 最大統一商機: {top_business.name} ({business_type_name})
- **低評分數量**: {int(top_business['low_rating_count'])} 個
- **低評分比率**: {top_business['low_rating_ratio']:.1f}%
- **總樣本數**: {int(top_business['total_count'])} 個
- **平均評分**: {top_business['avg_rating']:.2f} 星
- **商業類型**: {top_business['business_type']}
"""

        # 添加文件說明
        report_content += f"""

## 輸出檔案說明

### 圖表檔案 (`{ANALYSIS_CONFIG['charts_dir']}`)
- `rating_distribution.png`: 整體評分分布圖
- `business_low_count_opportunities.png`: 統一商機排行榜 (低評分數量)
- `business_low_ratio_opportunities.png`: 統一商機排行榜 (低評分比率)
- `business_opportunity_matrix.png`: 統一商機矩陣圖
- `dish_low_count_opportunities.png`: 料理低評分數量商機榜
- `dish_low_ratio_opportunities.png`: 料理低評分比率商機榜
- `dish_opportunity_matrix.png`: 料理商機矩陣圖
- `vendor_low_count_opportunities.png`: 店家低評分數量商機榜
- `vendor_low_ratio_opportunities.png`: 店家低評分比率商機榜
- `vendor_opportunity_matrix.png`: 店家商機矩陣圖

### 資料檔案 (`{ANALYSIS_CONFIG['data_dir']}`)
- `core_dataset.csv`: 核心分析資料集
- `business_low_count_opportunities.csv`: 統一低評分數量商機清單
- `business_low_ratio_opportunities.csv`: 統一低評分比率商機清單
- `business_high_count_competitors.csv`: 統一高評分競爭對手參考
- `dish_low_count_opportunities.csv`: 料理低評分數量商機清單
- `dish_low_ratio_opportunities.csv`: 料理低評分比率商機清單
- `vendor_low_count_opportunities.csv`: 店家低評分數量商機清單
- `vendor_low_ratio_opportunities.csv`: 店家低評分比率商機清單

## 建議行動方案

1. **優先關注低評分數量高的項目**: 這些代表市場需求大但品質不佳的領域
2. **研究低評分比率高的項目**: 這些代表評價普遍很差，有改善空間
3. **參考高評分競爭對手**: 了解市場標竿和品質期望
4. **詳細市場調研**: 針對發現的商機進行實地調查和驗證
5. **產品差異化**: 在發現的商機領域提供更優質的產品或服務

## 分析方法說明

### 商機識別邏輯
1. **低評分數量排行**: 識別獲得大量低評分的項目，代表市場需求大但現有產品品質不佳
2. **低評分比率排行**: 識別低評分比例高的項目，代表整體評價不佳的領域
3. **最少樣本數過濾**: 確保分析結果具有統計意義
4. **統一商機分析**: 將料理和店家統一分析，提供更全面的商機視角

### 數據品質保證
- 多表關聯驗證確保資料完整性
- 評分範圍檢查 (1-5星)
- 最少樣本數要求保證統計可靠性
- 商業標的分類確保分析準確性

---
*本報告由 Manager 餐廳評論商機發現分析系統自動生成*
*生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # 儲存報告
        report_filename = f'business_opportunity_report_{start_time.strftime("%Y%m%d_%H%M%S")}.md'
        report_path = os.path.join(self.output_dir, report_filename)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # 同時生成一個最新版本
        latest_report_path = os.path.join(self.output_dir, 'business_opportunity_report_latest.md')
        with open(latest_report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"摘要報告已生成: {report_path}")
        return report_path

    def generate_detailed_analysis_report(self, business_analysis, dish_analysis, vendor_analysis):
        """
        生成詳細分析報告

        Args:
            business_analysis (dict): 統一商機分析結果
            dish_analysis (dict): 料理分析結果
            vendor_analysis (dict): 店家分析結果

        Returns:
            str: 報告檔案路徑
        """
        logger.info("生成詳細分析報告...")

        report_content = "# 詳細商機分析報告\n\n"

        # 統一商機分析詳情
        if business_analysis:
            report_content += "## 統一商機分析\n\n"
            if not business_analysis['low_count_opportunities'].empty:
                report_content += "### 低評分數量商機排行榜\n\n"
                for idx, (name, row) in enumerate(business_analysis['low_count_opportunities'].iterrows(), 1):
                    business_type_name = "料理" if row['business_type'] == 'dish' else "店家"
                    report_content += f"{idx}. **{name}** ({business_type_name})\n"
                    report_content += f"   - 低評分數量: {int(row['low_rating_count'])} 個\n"
                    report_content += f"   - 低評分比率: {row['low_rating_ratio']:.1f}%\n"
                    report_content += f"   - 總樣本數: {int(row['total_count'])} 個\n"
                    report_content += f"   - 平均評分: {row['avg_rating']:.2f} 星\n\n"

        # 料理分析詳情
        if dish_analysis and not dish_analysis['low_count_opportunities'].empty:
            report_content += "## 料理商機分析\n\n"
            report_content += "### 料理低評分數量排行榜\n\n"
            for idx, (name, row) in enumerate(dish_analysis['low_count_opportunities'].iterrows(), 1):
                report_content += f"{idx}. **{name}**\n"
                report_content += f"   - 低評分數量: {int(row['low_rating_count'])} 個\n"
                report_content += f"   - 低評分比率: {row['low_rating_ratio']:.1f}%\n"
                report_content += f"   - 總樣本數: {int(row['total_count'])} 個\n"
                report_content += f"   - 平均評分: {row['avg_rating']:.2f} 星\n\n"

        # 店家分析詳情
        if vendor_analysis and not vendor_analysis['low_count_opportunities'].empty:
            report_content += "## 店家商機分析\n\n"
            report_content += "### 店家低評分數量排行榜\n\n"
            for idx, (name, row) in enumerate(vendor_analysis['low_count_opportunities'].iterrows(), 1):
                report_content += f"{idx}. **{name}**\n"
                report_content += f"   - 低評分數量: {int(row['low_rating_count'])} 個\n"
                report_content += f"   - 低評分比率: {row['low_rating_ratio']:.1f}%\n"
                report_content += f"   - 總樣本數: {int(row['total_count'])} 個\n"
                report_content += f"   - 平均評分: {row['avg_rating']:.2f} 星\n\n"

        report_content += f"""
---
*詳細分析報告由 Manager 餐廳評論商機發現分析系統自動生成*
*生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # 儲存詳細報告
        detailed_report_path = os.path.join(self.output_dir, 'detailed_analysis_report.md')
        with open(detailed_report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"詳細分析報告已生成: {detailed_report_path}")
        return detailed_report_path