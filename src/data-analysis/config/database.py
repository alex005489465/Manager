#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫配置模組

包含資料庫連接資訊和查詢相關配置
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

# 資料庫查詢配置
QUERY_CONFIG = {
    'batch_size': 1000,         # 批次處理大小
    'connection_timeout': 30,   # 連接超時秒數
    'query_timeout': 60         # 查詢超時秒數
}