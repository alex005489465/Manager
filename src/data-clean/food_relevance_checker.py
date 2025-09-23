#!/usr/bin/env python3
import mysql.connector
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
from config import DATABASE_CONFIG

# 載入環境變數
load_dotenv()

def setup_gemini():
    """設定 Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("請在 .env 檔案中設定 GEMINI_API_KEY")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    return model

def check_food_relevance(model, content):
    """使用 Gemini API 判別評論是否與食物相關"""
    prompt = f"""請判斷以下夜市評論是否與食物相關。
如果提到食物、菜品、口味、價格、份量等，回答 "Yes"
如果只談論環境、設施、管理、服務等，回答 "No"

評論：「{content}」

回答："""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()

        # 簡單的結果解析
        if 'Yes' in result or 'yes' in result or 'YES' in result:
            return True
        elif 'No' in result or 'no' in result or 'NO' in result:
            return False
        else:
            print(f"無法解析的回應: {result}")
            return None
    except Exception as e:
        print(f"API 呼叫錯誤: {e}")
        return None

def connect_database():
    """連接 MySQL 資料庫"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"資料庫連接錯誤: {e}")
        return None

def process_reviews():
    """處理評論資料"""
    # 設定 Gemini API
    try:
        model = setup_gemini()
        print("Gemini API 設定完成")
    except Exception as e:
        print(f"Gemini API 設定失敗: {e}")
        return

    # 連接資料庫
    conn = connect_database()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # 查詢所有需要處理的評論
        cursor.execute("""
            SELECT id, content
            FROM review_analysis
            WHERE is_project_related IS NULL
            ORDER BY id
        """)

        reviews = cursor.fetchall()
        total_reviews = len(reviews)
        print(f"找到 {total_reviews} 則需要處理的評論")

        if total_reviews == 0:
            print("沒有需要處理的評論")
            return

        # 處理每則評論
        processed = 0
        food_related = 0
        non_food_related = 0
        failed = 0

        for review_id, content in reviews:
            print(f"處理第 {processed + 1}/{total_reviews} 則評論 (ID: {review_id})")

            # 呼叫 Gemini API 判別
            is_food_related = check_food_relevance(model, content)

            if is_food_related is not None:
                # 更新資料庫
                cursor.execute("""
                    UPDATE review_analysis
                    SET is_project_related = %s
                    WHERE id = %s
                """, (is_food_related, review_id))

                if is_food_related:
                    food_related += 1
                else:
                    non_food_related += 1

                processed += 1

                # 每處理 10 則評論就提交一次
                if processed % 10 == 0:
                    conn.commit()
                    print(f"已處理 {processed} 則評論，已提交資料庫")

                # 加入延遲避免超過 API 限制（免費層級每分鐘 15 次）
                # 每處理一則評論後等待 5 秒，確保不超過限制
                time.sleep(5)
            else:
                failed += 1
                print(f"第 {processed + 1} 則評論處理失敗")
                # 失敗時也要延遲，避免連續失敗
                time.sleep(5)

        # 最終提交
        conn.commit()

        # 顯示統計結果
        print(f"\n處理完成！")
        print(f"總共處理: {processed} 則評論")
        print(f"與食物相關: {food_related} 則")
        print(f"與食物無關: {non_food_related} 則")
        print(f"處理失敗: {failed} 則")

        # 驗證結果
        cursor.execute("""
            SELECT
                is_project_related,
                COUNT(*) as count
            FROM review_analysis
            GROUP BY is_project_related
        """)

        print(f"\n資料庫統計:")
        for result in cursor.fetchall():
            status = result[0]
            count = result[1]
            if status is None:
                print(f"未處理: {count} 則")
            elif status:
                print(f"食物相關: {count} 則")
            else:
                print(f"非食物相關: {count} 則")

    except Exception as e:
        print(f"處理錯誤: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("開始食物相關性判別處理...")
    process_reviews()
    print("處理完成！")