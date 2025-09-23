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

def check_food_relevance_batch(model, review_batch):
    """使用 Gemini API 批次判別評論是否與食物相關"""
    # 建立批次 prompt
    prompt = "請判斷以下夜市評論是否與食物相關，對每則評論回答 Yes 或 No。\n\n"

    for i, (review_id, content) in enumerate(review_batch, 1):
        prompt += f"評論{i}：「{content}」\n"

    prompt += f"\n請按順序回答（只要數字和答案）：\n"
    for i in range(1, len(review_batch) + 1):
        prompt += f"{i}. Yes/No\n"

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()

        # 解析批次結果
        lines = result.split('\n')
        results = []

        for i, line in enumerate(lines):
            line = line.strip()
            if line and (str(i+1) in line or f"{i+1}." in line):
                if 'Yes' in line or 'yes' in line or 'YES' in line:
                    results.append(True)
                elif 'No' in line or 'no' in line or 'NO' in line:
                    results.append(False)
                else:
                    results.append(None)

        # 確保結果數量正確
        if len(results) != len(review_batch):
            print(f"批次結果數量不符: 預期 {len(review_batch)}，得到 {len(results)}")
            print(f"原始回應: {result}")
            return None

        return results
    except Exception as e:
        print(f"批次 API 呼叫錯誤: {e}")
        return None

def check_food_relevance(model, content):
    """使用 Gemini API 判別單則評論是否與食物相關（備用方法）"""
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
    """處理評論資料（批次處理版本）"""
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

        # 批次處理設定
        batch_size = 15
        processed = 0
        food_related = 0
        non_food_related = 0
        failed = 0

        # 分批處理評論
        for i in range(0, total_reviews, batch_size):
            batch = reviews[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_reviews + batch_size - 1) // batch_size

            print(f"\n處理第 {batch_num}/{total_batches} 批次 ({len(batch)} 則評論)")

            # 批次 API 呼叫
            batch_results = check_food_relevance_batch(model, batch)

            if batch_results is not None and len(batch_results) == len(batch):
                # 批次處理成功
                for j, (review_id, content) in enumerate(batch):
                    is_food_related = batch_results[j]

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

                # 提交批次結果
                conn.commit()
                print(f"批次 {batch_num} 處理完成，已更新資料庫")

                # 批次間延遲（避免 API 限制）
                if batch_num < total_batches:
                    time.sleep(5)
            else:
                # 批次處理失敗，回退到逐則處理
                print(f"批次 {batch_num} 處理失敗，回退到逐則處理")

                for review_id, content in batch:
                    print(f"  處理評論 ID: {review_id}")

                    is_food_related = check_food_relevance(model, content)

                    if is_food_related is not None:
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
                        time.sleep(2)  # 較短的延遲
                    else:
                        failed += 1
                        print(f"  評論 ID {review_id} 處理失敗")

                conn.commit()

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