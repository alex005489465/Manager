#!/usr/bin/env python3
import json
import os
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG

def connect_database():
    """連接MySQL資料庫"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"資料庫連接錯誤: {e}")
        return None

def insert_search_metadata(cursor, data, search_id):
    """插入搜尋元數據"""
    place_info = data.get('place_info', {})
    search_metadata = data.get('search_metadata', {})
    search_parameters = data.get('search_parameters', {})

    sql = """
    INSERT INTO search_metadata
    (search_id, google_maps_reviews_url, data_id, title, address, rating, reviews)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        search_id,
        search_metadata.get('google_maps_reviews_url'),
        search_parameters.get('data_id'),
        place_info.get('title'),
        place_info.get('address'),
        place_info.get('rating'),
        place_info.get('reviews')
    )

    cursor.execute(sql, values)

def convert_iso_date(iso_string):
    """轉換ISO日期格式為MySQL TIMESTAMP格式"""
    if not iso_string:
        return None
    try:
        # 將ISO格式轉換為MySQL TIMESTAMP格式
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def insert_reviews(cursor, reviews_data, search_id):
    """批次插入評論資料"""
    if not reviews_data:
        return

    sql = """
    INSERT INTO reviews
    (review_id, search_id, rating, snippet, link, iso_date, iso_date_of_last_edit)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values_list = []
    for review in reviews_data:
        values = (
            review.get('review_id'),
            search_id,
            review.get('rating'),
            review.get('snippet'),
            review.get('link'),
            convert_iso_date(review.get('iso_date')),
            convert_iso_date(review.get('iso_date_of_last_edit'))
        )
        values_list.append(values)

    cursor.executemany(sql, values_list)

def process_json_files():
    """處理所有JSON檔案"""
    data_dir = './data/raw/'
    search_id = 'yongda_night_market_2025'

    conn = connect_database()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # 找到所有JSON檔案
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        json_files.sort()  # 確保順序

        print(f"找到 {len(json_files)} 個JSON檔案")

        # 插入search_metadata (只需要一次，使用第一個檔案)
        if json_files:
            first_file = os.path.join(data_dir, json_files[0])
            with open(first_file, 'r', encoding='utf-8') as f:
                first_data = json.load(f)

            print("插入搜尋元數據...")
            insert_search_metadata(cursor, first_data, search_id)

        # 處理所有檔案的評論資料
        total_reviews = 0
        for i, filename in enumerate(json_files, 1):
            file_path = os.path.join(data_dir, filename)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            reviews = data.get('reviews', [])
            if reviews:
                insert_reviews(cursor, reviews, search_id)
                total_reviews += len(reviews)

            print(f"處理第 {i}/{len(json_files)} 個檔案: {filename} ({len(reviews)} 則評論)")

        # 提交變更
        conn.commit()
        print(f"\n資料匯入完成！")
        print(f"- 搜尋元數據: 1 筆")
        print(f"- 評論資料: {total_reviews} 筆")

    except Exception as e:
        print(f"錯誤: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    process_json_files()