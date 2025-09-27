#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基礎圖表模組

提供所有圖表的基礎抽象類別和共用功能
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import os
import logging
from abc import ABC, abstractmethod
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import CHART_CONFIG

# 設定日誌
logger = logging.getLogger(__name__)

# 設定警告抑制
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')

# 導入字體管理模組
import matplotlib.font_manager as fm


class BaseChart(ABC):
    """基礎圖表抽象類別"""

    def __init__(self, output_dir=None):
        """
        初始化基礎圖表

        Args:
            output_dir (str): 輸出目錄，預設使用配置中的目錄
        """
        from config import ANALYSIS_CONFIG
        self.output_dir = output_dir or ANALYSIS_CONFIG['charts_dir']
        os.makedirs(self.output_dir, exist_ok=True)

        # 設定圖表樣式
        plt.style.use('default')  # 改用 default 樣式避免 seaborn 版本問題
        sns.set_palette(CHART_CONFIG['color_palette'])

        # 重新設定中文字體（必須在 plt.style.use 之後）
        self._setup_chinese_font()
        matplotlib.rcParams['axes.unicode_minus'] = False

    def _setup_chinese_font(self):
        """設定中文字體，僅使用專案內字體檔案"""
        # 計算字體檔案路徑
        font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')
        font_path = os.path.join(font_dir, 'NotoSansCJK-Regular.ttc')

        # 檢查字體檔案是否存在
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"專案字體檔案不存在: {font_path}")

        # 註冊專案內字體
        try:
            fm.fontManager.addfont(font_path)
        except Exception as e:
            raise RuntimeError(f"無法註冊專案字體檔案 {font_path}: {e}")

        # 取得字體屬性
        try:
            font_prop = fm.FontProperties(fname=font_path)
            font_name = font_prop.get_name()
        except Exception as e:
            raise RuntimeError(f"無法讀取字體屬性 {font_path}: {e}")

        # 僅設定專案字體
        matplotlib.rcParams['font.sans-serif'] = [font_name]
        matplotlib.rcParams['font.family'] = 'sans-serif'

        logger.info(f"專案字體設定成功: {font_name} (來源: {font_path})")

    def save_chart(self, filename, dpi=None, bbox_inches='tight'):
        """
        儲存圖表

        Args:
            filename (str): 檔案名稱
            dpi (int): 解析度
            bbox_inches (str): 邊界設定
        """
        if dpi is None:
            dpi = CHART_CONFIG['dpi']

        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
        plt.close()
        logger.info(f"圖表已儲存: {output_path}")
        return output_path

    def setup_figure(self, figsize=None):
        """
        設定圖表大小

        Args:
            figsize (tuple): 圖表大小，預設使用配置值
        """
        if figsize is None:
            figsize = CHART_CONFIG['figure_size']
        plt.figure(figsize=figsize)

    def add_title(self, title, fontsize=None, fontweight='bold'):
        """
        添加標題

        Args:
            title (str): 標題文字
            fontsize (int): 字體大小
            fontweight (str): 字體粗細
        """
        if fontsize is None:
            fontsize = CHART_CONFIG['title_size']
        plt.title(title, fontsize=fontsize, fontweight=fontweight)

    def add_labels(self, xlabel=None, ylabel=None, fontsize=None):
        """
        添加軸標籤

        Args:
            xlabel (str): X軸標籤
            ylabel (str): Y軸標籤
            fontsize (int): 字體大小
        """
        if fontsize is None:
            fontsize = CHART_CONFIG['font_size']

        if xlabel:
            plt.xlabel(xlabel, fontsize=fontsize)
        if ylabel:
            plt.ylabel(ylabel, fontsize=fontsize)

    def add_value_labels(self, bars, values, offset_x=0.05, offset_y=0, fontsize=9, ha='left', va='center'):
        """
        在長條圖上添加數值標籤

        Args:
            bars: 長條圖物件
            values: 數值列表
            offset_x (float): X方向偏移
            offset_y (float): Y方向偏移
            fontsize (int): 字體大小
            ha (str): 水平對齊
            va (str): 垂直對齊
        """
        for bar, value in zip(bars, values):
            plt.text(
                bar.get_width() + offset_x,
                bar.get_y() + bar.get_height()/2 + offset_y,
                f'{value:.1f}',
                ha=ha, va=va, fontsize=fontsize
            )

    def apply_layout(self):
        """應用布局調整"""
        plt.tight_layout()

    def validate_data(self, data):
        """
        驗證資料有效性

        Args:
            data: 要驗證的資料

        Raises:
            ValueError: 當資料無效時
        """
        if data is None or (hasattr(data, 'empty') and data.empty):
            raise ValueError("資料不能為空")

    @abstractmethod
    def plot(self, data, title, filename, **kwargs):
        """
        繪製圖表（由子類別實作）

        Args:
            data: 圖表資料
            title (str): 圖表標題
            filename (str): 儲存檔名
            **kwargs: 其他參數
        """
        pass