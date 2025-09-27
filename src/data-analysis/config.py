#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料分析工具配置檔案

包含資料庫連接資訊和分析參數設定
"""

# 資料庫連接配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'manager_reviews_db',
    'user': 'manager_reviews_user',
    'password': 'MgrRev2024!@#',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': True
}

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

# 圖表配置
CHART_CONFIG = {
    'figure_size': (12, 8),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'viridis',
    'font_size': 12,
    'title_size': 16
}

# 資料庫查詢配置
QUERY_CONFIG = {
    'batch_size': 1000,         # 批次處理大小
    'connection_timeout': 30,   # 連接超時秒數
    'query_timeout': 60         # 查詢超時秒數
}