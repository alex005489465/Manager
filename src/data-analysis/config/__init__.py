#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模組

提供分層的配置管理，包含資料庫、分析、視覺化等配置
"""

from .database import DATABASE_CONFIG, QUERY_CONFIG
from .analysis import ANALYSIS_CONFIG
from .visualization import CHART_CONFIG

__all__ = [
    'DATABASE_CONFIG',
    'QUERY_CONFIG',
    'ANALYSIS_CONFIG',
    'CHART_CONFIG'
]