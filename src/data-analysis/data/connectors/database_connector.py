#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫連接管理模組

提供 MySQL 資料庫連接和查詢功能
"""

import mysql.connector
import pandas as pd
from contextlib import contextmanager
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import DATABASE_CONFIG, QUERY_CONFIG

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseConnector:
    """資料庫連接管理類別"""

    def __init__(self, config=None):
        """
        初始化資料庫連接器

        Args:
            config (dict): 資料庫配置，預設使用 DATABASE_CONFIG
        """
        self.config = config if config is not None else DATABASE_CONFIG
        self.connection = None

    def connect(self):
        """
        建立資料庫連接

        Returns:
            mysql.connector.connection: 資料庫連接物件
        """
        try:
            connection = mysql.connector.connect(
                **self.config,
                connection_timeout=QUERY_CONFIG['connection_timeout']
            )
            logger.info("資料庫連接成功")
            return connection
        except mysql.connector.Error as e:
            logger.error(f"資料庫連接錯誤: {e}")
            raise Exception(f"資料庫連接失敗: {e}")

    @contextmanager
    def get_connection(self):
        """
        取得資料庫連接的上下文管理器

        Yields:
            mysql.connector.connection: 資料庫連接物件
        """
        conn = None
        try:
            conn = self.connect()
            yield conn
        finally:
            if conn and conn.is_connected():
                conn.close()
                logger.debug("資料庫連接已關閉")

    def execute_query(self, query, params=None):
        """
        執行查詢並返回 pandas DataFrame

        Args:
            query (str): SQL 查詢語句
            params (tuple): 查詢參數

        Returns:
            pd.DataFrame: 查詢結果
        """
        try:
            with self.get_connection() as conn:
                logger.info(f"執行查詢: {query[:100]}...")
                df = pd.read_sql(query, conn, params=params)
                logger.info(f"查詢完成，返回 {len(df)} 筆記錄")
                return df
        except Exception as e:
            logger.error(f"查詢執行錯誤: {e}")
            raise

    def execute_custom_query(self, query, params=None, fetch_all=True):
        """
        執行自定義查詢並返回原始結果

        Args:
            query (str): SQL 查詢語句
            params (tuple): 查詢參數
            fetch_all (bool): 是否取得所有結果

        Returns:
            list or tuple: 查詢結果
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

                if fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()

                cursor.close()
                return result
        except Exception as e:
            logger.error(f"自定義查詢錯誤: {e}")
            raise

    def test_connection(self):
        """
        測試資料庫連接

        Returns:
            bool: 連接是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()

                if result and result[0] == 1:
                    logger.info("資料庫連接測試成功")
                    return True
                else:
                    logger.error("資料庫連接測試失敗")
                    return False
        except Exception as e:
            logger.error(f"資料庫連接測試錯誤: {e}")
            return False

    def get_table_info(self, table_name):
        """
        取得資料表資訊

        Args:
            table_name (str): 資料表名稱

        Returns:
            pd.DataFrame: 資料表結構資訊
        """
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)

    def get_table_count(self, table_name):
        """
        取得資料表記錄數

        Args:
            table_name (str): 資料表名稱

        Returns:
            int: 記錄數
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result.iloc[0]['count'] if not result.empty else 0


# 建立全域資料庫連接器實例
db_connector = DatabaseConnector()


def get_db_connector():
    """
    取得資料庫連接器實例

    Returns:
        DatabaseConnector: 資料庫連接器
    """
    return db_connector


if __name__ == "__main__":
    # 測試資料庫連接
    print("測試資料庫連接...")

    connector = DatabaseConnector()

    if connector.test_connection():
        print(">> 資料庫連接測試成功")

        # 測試查詢資料表資訊
        try:
            tables = ['extracted_food_items', 'review_analysis', 'reviews']
            for table in tables:
                count = connector.get_table_count(table)
                print(f">> {table} 表有 {count} 筆記錄")
        except Exception as e:
            print(f">> 查詢資料表資訊失敗: {e}")
    else:
        print(">> 資料庫連接測試失敗")