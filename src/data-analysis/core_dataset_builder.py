#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心資料集建立模組

負責執行多表關聯查詢，建立包含 extracted_food_items + reviews.rating 的核心分析資料集
"""

import pandas as pd
import logging
from database_connector import get_db_connector
from config import ANALYSIS_CONFIG
import os

# 設定日誌
logger = logging.getLogger(__name__)


class CoreDatasetBuilder:
    """核心資料集建立器"""

    def __init__(self):
        """初始化資料集建立器"""
        self.db = get_db_connector()
        self.core_dataset = None

    def build_core_dataset(self):
        """
        建立核心資料集：extracted_food_items + reviews.rating

        關聯路徑：
        extracted_food_items.review_id → review_analysis.id → review_analysis.review_id → reviews.id → reviews.rating

        Returns:
            pd.DataFrame: 核心資料集
        """
        logger.info("開始建立核心資料集...")

        # 核心資料集 SQL 查詢
        query = """
        SELECT
            e.id as item_id,
            e.dish_name,
            e.vendor_name,
            e.price,
            e.rating_sentiment,
            e.data_completeness,
            r.rating,
            r.iso_date
        FROM extracted_food_items e
        JOIN review_analysis ra ON e.review_id = ra.id
        JOIN reviews r ON ra.review_id = r.id
        WHERE r.rating IS NOT NULL
            AND e.dish_name IS NOT NULL
        ORDER BY e.id
        """

        try:
            self.core_dataset = self.db.execute_query(query)
            logger.info(f"核心資料集建立完成，共 {len(self.core_dataset)} 筆記錄")

            # 資料品質檢查
            self._validate_dataset()

            return self.core_dataset

        except Exception as e:
            logger.error(f"核心資料集建立失敗: {e}")
            raise

    def _validate_dataset(self):
        """驗證資料集品質"""
        if self.core_dataset is None:
            raise ValueError("資料集尚未建立")

        total_records = len(self.core_dataset)
        logger.info(f"資料集驗證 - 總記錄數: {total_records}")

        # 檢查必要欄位
        required_columns = ['dish_name', 'rating']
        missing_columns = [col for col in required_columns if col not in self.core_dataset.columns]
        if missing_columns:
            raise ValueError(f"缺少必要欄位: {missing_columns}")

        # 檢查評分範圍
        invalid_ratings = self.core_dataset[
            (self.core_dataset['rating'] < 1) | (self.core_dataset['rating'] > 5)
        ]
        if not invalid_ratings.empty:
            logger.warning(f"發現 {len(invalid_ratings)} 筆評分超出範圍 (1-5) 的記錄")

        # 統計資料完整度
        dish_null_count = self.core_dataset['dish_name'].isnull().sum()
        vendor_null_count = self.core_dataset['vendor_name'].isnull().sum()
        price_null_count = self.core_dataset['price'].isnull().sum()

        logger.info(f"資料完整度:")
        logger.info(f"  - 料理名稱缺失: {dish_null_count} 筆 ({dish_null_count/total_records*100:.1f}%)")
        logger.info(f"  - 店家名稱缺失: {vendor_null_count} 筆 ({vendor_null_count/total_records*100:.1f}%)")
        logger.info(f"  - 價格資訊缺失: {price_null_count} 筆 ({price_null_count/total_records*100:.1f}%)")

    def get_basic_statistics(self):
        """
        取得基礎統計資訊

        Returns:
            dict: 統計資訊
        """
        if self.core_dataset is None:
            raise ValueError("資料集尚未建立")

        stats = {
            'total_items': len(self.core_dataset),
            'unique_dishes': self.core_dataset['dish_name'].nunique(),
            'unique_vendors': self.core_dataset['vendor_name'].nunique(),
            'avg_rating': self.core_dataset['rating'].mean(),
            'rating_distribution': self.core_dataset['rating'].value_counts().sort_index().to_dict(),
            'completion_rate': {
                'dish_name': (self.core_dataset['dish_name'].notnull().sum() / len(self.core_dataset)) * 100,
                'vendor_name': (self.core_dataset['vendor_name'].notnull().sum() / len(self.core_dataset)) * 100,
                'price': (self.core_dataset['price'].notnull().sum() / len(self.core_dataset)) * 100
            }
        }

        return stats

    def export_dataset(self, filename='core_dataset.csv'):
        """
        匯出核心資料集到 CSV

        Args:
            filename (str): 檔案名稱
        """
        if self.core_dataset is None:
            raise ValueError("資料集尚未建立")

        # 確保輸出目錄存在
        output_path = os.path.join(ANALYSIS_CONFIG['data_dir'], filename)
        os.makedirs(ANALYSIS_CONFIG['data_dir'], exist_ok=True)

        self.core_dataset.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"核心資料集已匯出至: {output_path}")

        return output_path

    def get_dataset(self):
        """
        取得核心資料集

        Returns:
            pd.DataFrame: 核心資料集
        """
        return self.core_dataset

    def filter_by_min_samples(self, column, min_samples):
        """
        過濾最少樣本數

        Args:
            column (str): 過濾欄位 ('dish_name' 或 'vendor_name')
            min_samples (int): 最少樣本數

        Returns:
            pd.DataFrame: 過濾後的資料集
        """
        if self.core_dataset is None:
            raise ValueError("資料集尚未建立")

        # 計算每個項目的樣本數
        item_counts = self.core_dataset[column].value_counts()
        valid_items = item_counts[item_counts >= min_samples].index

        # 過濾資料集
        filtered_dataset = self.core_dataset[self.core_dataset[column].isin(valid_items)]

        logger.info(f"按 {column} 過濾 (最少 {min_samples} 樣本): {len(filtered_dataset)} 筆記錄")

        return filtered_dataset


if __name__ == "__main__":
    # 測試核心資料集建立
    print("測試核心資料集建立...")

    builder = CoreDatasetBuilder()

    try:
        # 建立核心資料集
        dataset = builder.build_core_dataset()
        print(f">> 核心資料集建立成功: {len(dataset)} 筆記錄")

        # 顯示基礎統計
        stats = builder.get_basic_statistics()
        print(f">> 唯一料理數: {stats['unique_dishes']}")
        print(f">> 唯一店家數: {stats['unique_vendors']}")
        print(f">> 平均評分: {stats['avg_rating']:.2f}")

        # 匯出資料集
        output_file = builder.export_dataset()
        print(f">> 資料集已匯出至: {output_file}")

        # 顯示前幾筆資料
        print("\n>> 前5筆資料:")
        print(dataset.head().to_string())

    except Exception as e:
        print(f">> 核心資料集建立失敗: {e}")
        logger.error(f"測試失敗: {e}", exc_info=True)