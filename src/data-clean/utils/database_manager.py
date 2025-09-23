"""
資料庫管理工具

提供資料庫連接和操作的封裝功能
"""

import mysql.connector
from contextlib import contextmanager
from config import DATABASE_CONFIG

class DatabaseManager:
    """資料庫管理類別"""

    def __init__(self, config=None):
        """
        初始化資料庫管理器

        Args:
            config (dict): 資料庫配置，預設使用 DATABASE_CONFIG
        """
        self.config = config if config is not None else DATABASE_CONFIG

    def connect(self):
        """
        建立資料庫連接

        Returns:
            mysql.connector.connection: 資料庫連接物件
        """
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as e:
            raise Exception(f"資料庫連接錯誤: {e}")

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
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self, connection=None):
        """
        取得資料庫游標的上下文管理器

        Args:
            connection: 現有的資料庫連接，如為 None 則自動建立

        Yields:
            mysql.connector.cursor: 資料庫游標物件
        """
        if connection:
            cursor = connection.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    yield cursor
                finally:
                    cursor.close()

    def execute_query(self, query, params=None, fetch_all=True):
        """
        執行查詢並返回結果

        Args:
            query (str): SQL 查詢語句
            params (tuple): 查詢參數
            fetch_all (bool): 是否取得所有結果

        Returns:
            list or tuple: 查詢結果
        """
        with self.get_connection() as conn:
            with self.get_cursor(conn) as cursor:
                cursor.execute(query, params)
                if fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()

    def execute_update(self, query, params=None, commit=True):
        """
        執行更新操作

        Args:
            query (str): SQL 更新語句
            params (tuple): 更新參數
            commit (bool): 是否自動提交

        Returns:
            int: 受影響的行數
        """
        with self.get_connection() as conn:
            with self.get_cursor(conn) as cursor:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                return cursor.rowcount

    def execute_batch_update(self, query, params_list, commit=True):
        """
        執行批次更新操作

        Args:
            query (str): SQL 更新語句
            params_list (list): 參數列表
            commit (bool): 是否自動提交

        Returns:
            int: 受影響的總行數
        """
        with self.get_connection() as conn:
            with self.get_cursor(conn) as cursor:
                cursor.executemany(query, params_list)
                if commit:
                    conn.commit()
                return cursor.rowcount

class ReviewAnalysisManager(DatabaseManager):
    """評論分析表專用的資料庫管理器"""

    def get_food_related_reviews(self, limit=None):
        """
        取得食物相關的評論

        Args:
            limit (int): 限制返回數量

        Returns:
            list: 評論列表 [(id, content), ...]
        """
        query = """
            SELECT id, content
            FROM review_analysis
            WHERE is_project_related = TRUE
                AND has_specific_food_mention IS NULL
            ORDER BY id
        """

        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query)

    def get_unprocessed_reviews(self, limit=None):
        """
        取得未處理的評論

        Args:
            limit (int): 限制返回數量

        Returns:
            list: 評論列表 [(id, content), ...]
        """
        query = """
            SELECT id, content
            FROM review_analysis
            WHERE is_project_related IS NULL
            ORDER BY id
        """

        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query)

    def update_food_relevance(self, review_id, is_food_related):
        """
        更新食物相關性

        Args:
            review_id (int): 評論 ID
            is_food_related (bool): 是否與食物相關

        Returns:
            int: 受影響的行數
        """
        query = """
            UPDATE review_analysis
            SET is_project_related = %s
            WHERE id = %s
        """
        return self.execute_update(query, (is_food_related, review_id))

    def update_specific_food_mention(self, review_id, has_specific_mention):
        """
        更新具體食物提及狀況

        Args:
            review_id (int): 評論 ID
            has_specific_mention (bool): 是否提到具體食物

        Returns:
            int: 受影響的行數
        """
        query = """
            UPDATE review_analysis
            SET has_specific_food_mention = %s
            WHERE id = %s
        """
        return self.execute_update(query, (has_specific_mention, review_id))

    def batch_update_food_relevance(self, updates):
        """
        批次更新食物相關性

        Args:
            updates (list): 更新列表 [(is_food_related, review_id), ...]

        Returns:
            int: 受影響的行數
        """
        query = """
            UPDATE review_analysis
            SET is_project_related = %s
            WHERE id = %s
        """
        return self.execute_batch_update(query, updates)

    def batch_update_specific_food_mention(self, updates):
        """
        批次更新具體食物提及狀況

        Args:
            updates (list): 更新列表 [(has_specific_mention, review_id), ...]

        Returns:
            int: 受影響的行數
        """
        query = """
            UPDATE review_analysis
            SET has_specific_food_mention = %s
            WHERE id = %s
        """
        return self.execute_batch_update(query, updates)

    def get_analysis_statistics(self):
        """
        取得分析統計資訊

        Returns:
            dict: 統計資訊
        """
        # 基礎統計
        total_query = "SELECT COUNT(*) FROM review_analysis"
        total_count = self.execute_query(total_query, fetch_all=False)[0]

        # 食物相關性統計
        food_stats_query = """
            SELECT
                is_project_related,
                COUNT(*) as count
            FROM review_analysis
            GROUP BY is_project_related
        """
        food_stats = self.execute_query(food_stats_query)

        # 具體食物提及統計
        specific_stats_query = """
            SELECT
                has_specific_food_mention,
                COUNT(*) as count
            FROM review_analysis
            WHERE is_project_related = TRUE
            GROUP BY has_specific_food_mention
        """
        specific_stats = self.execute_query(specific_stats_query)

        return {
            'total_reviews': total_count,
            'food_relevance_stats': food_stats,
            'specific_food_stats': specific_stats
        }

    def get_sample_reviews(self, category='all', limit=5):
        """
        取得樣本評論

        Args:
            category (str): 評論類別 ('food_related', 'non_food', 'specific_food', 'general_food', 'all')
            limit (int): 樣本數量

        Returns:
            list: 樣本評論
        """
        base_query = "SELECT id, LEFT(content, 100) as preview FROM review_analysis"

        if category == 'food_related':
            query = f"{base_query} WHERE is_project_related = TRUE ORDER BY id LIMIT {limit}"
        elif category == 'non_food':
            query = f"{base_query} WHERE is_project_related = FALSE ORDER BY id LIMIT {limit}"
        elif category == 'specific_food':
            query = f"{base_query} WHERE is_project_related = TRUE AND has_specific_food_mention = TRUE ORDER BY id LIMIT {limit}"
        elif category == 'general_food':
            query = f"{base_query} WHERE is_project_related = TRUE AND has_specific_food_mention = FALSE ORDER BY id LIMIT {limit}"
        else:
            query = f"{base_query} ORDER BY id LIMIT {limit}"

        return self.execute_query(query)