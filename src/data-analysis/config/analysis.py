#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析配置模組

包含商機分析參數和閾值設定
"""

# 商機分析參數
ANALYSIS_CONFIG = {
    # 低評分定義 (1-2 星)
    'low_rating_threshold': 2,

    # 高評分定義 (4-5 星)
    'high_rating_threshold': 4,

    # 最少樣本數要求
    'min_samples_dish': 5,      # 料理最少樣本數
    'min_samples_vendor': 3,    # 店家最少樣本數

    # 排行榜數量
    'top_n_items': 10,

    # 輸出目錄
    'output_dir': './output',
    'charts_dir': './output/charts',
    'reports_dir': './output/reports',
    'data_dir': './output/data'
}