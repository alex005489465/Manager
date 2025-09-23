#!/usr/bin/env python3
import mysql.connector
from config import DATABASE_CONFIG

def verify_import():
    """驗證資料匯入結果"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # 檢查search_metadata表
        cursor.execute("SELECT COUNT(*) FROM search_metadata")
        search_count = cursor.fetchone()[0]
        print(f"search_metadata 表記錄數: {search_count}")

        # 檢查reviews表
        cursor.execute("SELECT COUNT(*) FROM reviews")
        reviews_count = cursor.fetchone()[0]
        print(f"reviews 表記錄數: {reviews_count}")

        # 顯示search_metadata詳細資訊
        cursor.execute("SELECT * FROM search_metadata LIMIT 1")
        search_data = cursor.fetchone()
        if search_data:
            print(f"\n搜尋元數據:")
            print(f"- 地點名稱: {search_data[4]}")  # title
            print(f"- 地址: {search_data[5]}")      # address
            print(f"- 評分: {search_data[6]}")      # rating
            print(f"- 總評論數: {search_data[7]}")   # reviews

        # 顯示部分評論資料
        cursor.execute("SELECT review_id, rating, snippet FROM reviews LIMIT 3")
        review_samples = cursor.fetchall()
        print(f"\n評論範例:")
        for i, review in enumerate(review_samples, 1):
            snippet = review[2][:100] + "..." if review[2] and len(review[2]) > 100 else review[2]
            print(f"{i}. 評分: {review[1]}, 內容: {snippet}")

        # 檢查日期範圍
        cursor.execute("SELECT MIN(iso_date), MAX(iso_date) FROM reviews WHERE iso_date IS NOT NULL")
        date_range = cursor.fetchone()
        if date_range[0]:
            print(f"\n評論時間範圍: {date_range[0]} 至 {date_range[1]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"驗證錯誤: {e}")

if __name__ == "__main__":
    verify_import()