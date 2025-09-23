#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from config import DATABASE_CONFIG

def export_specific_food_content():
    try:
        # 連接資料庫
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        # 查詢 has_specific_food_mention = 1 的內容
        query = """
        SELECT content
        FROM review_analysis
        WHERE has_specific_food_mention = 1
        ORDER BY id
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # 寫入 md 檔案
        with open('specific_food_mentions.md', 'w', encoding='utf-8') as f:
            for i, (content,) in enumerate(results, 1):
                f.write(f"{i}. {content}\n\n")

        print(f"已匯出 {len(results)} 則具體食物評論到 specific_food_mentions.md")

    except mysql.connector.Error as err:
        print(f"資料庫錯誤: {err}")
    except Exception as e:
        print(f"執行錯誤: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    export_specific_food_content()