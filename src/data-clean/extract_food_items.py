#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import google.generativeai as genai
import json
import time
import logging
from config import DATABASE_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extract_food_items.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 設定 Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# 提取 Prompt 模板
EXTRACTION_PROMPT = """
從評論中提取食物相關資訊，返回JSON格式。

評論：{content}

請提取：
- dish_name: 料理名稱（如：臭豆腐）
- vendor_name: 店家名稱（如：326臭臭鍋）
- description: 描述內容
- price: 價格（如：40元）
- rating_sentiment: positive/negative/neutral
- data_completeness: complete/partial/minimal

返回格式：
{{"items": [{{"dish_name": "料理名稱", "vendor_name": "店家名稱", "description": "描述", "price": "價格", "rating_sentiment": "positive", "data_completeness": "partial"}}]}}

如果沒有項目，返回：{{"items": []}}
"""

def get_pending_reviews(batch_size=10):
    """取得待處理的評論"""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT id, content
        FROM review_analysis
        WHERE has_specific_food_mention = TRUE
            AND (is_food_items_extracted = FALSE OR is_food_items_extracted IS NULL)
        ORDER BY id
        LIMIT %s
        """

        cursor.execute(query, (batch_size,))
        results = cursor.fetchall()

        return results

    except mysql.connector.Error as err:
        logging.error(f"資料庫查詢錯誤: {err}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def extract_food_items_with_llm(content):
    """使用 LLM 提取食物項目"""
    try:
        prompt = EXTRACTION_PROMPT.format(content=content)
        response = model.generate_content(prompt)

        # 清理回應內容，移除可能的 markdown 格式
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        # 解析 JSON
        result = json.loads(response_text)

        # 驗證結構
        if 'items' not in result:
            logging.warning(f"LLM 回應格式錯誤，缺少 items 欄位")
            return []

        return result['items']

    except json.JSONDecodeError as e:
        logging.error(f"JSON 解析錯誤: {e}")
        logging.error(f"清理後的回應: {response_text}")
        logging.error(f"原始回應: {response.text}")
        return []
    except Exception as e:
        logging.error(f"LLM 提取錯誤: {e}")
        return []

def save_extracted_items(review_id, items):
    """儲存提取的食物項目到資料庫"""
    connection = None
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        # 開始事務
        connection.start_transaction()

        # 插入提取的項目
        insert_query = """
        INSERT INTO extracted_food_items
        (review_id, dish_name, vendor_name, description, price, rating_sentiment, data_completeness)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for item in items:
            cursor.execute(insert_query, (
                review_id,
                item.get('dish_name'),
                item.get('vendor_name'),
                item.get('description'),
                item.get('price'),
                item.get('rating_sentiment'),
                item.get('data_completeness', 'partial')
            ))

        # 更新處理狀態
        update_query = """
        UPDATE review_analysis
        SET is_food_items_extracted = TRUE
        WHERE id = %s
        """
        cursor.execute(update_query, (review_id,))

        # 提交事務
        connection.commit()

        logging.info(f"成功處理評論 {review_id}，提取 {len(items)} 個食物項目")
        return True

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        logging.error(f"資料庫儲存錯誤: {err}")
        return False
    except Exception as e:
        if connection:
            connection.rollback()
        logging.error(f"儲存過程錯誤: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection:
            connection.close()

def mark_as_processed_only(review_id):
    """僅標記為已處理（當沒有提取到任何項目時）"""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        update_query = """
        UPDATE review_analysis
        SET is_food_items_extracted = TRUE
        WHERE id = %s
        """
        cursor.execute(update_query, (review_id,))
        connection.commit()

        logging.info(f"評論 {review_id} 已標記為已處理（無提取項目）")
        return True

    except mysql.connector.Error as err:
        logging.error(f"標記處理狀態錯誤: {err}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def main():
    """主要執行函數"""
    logging.info("開始食物項目提取程序")

    total_processed = 0
    total_extracted = 0

    while True:
        # 取得一批待處理的評論
        reviews = get_pending_reviews(batch_size=10)

        if not reviews:
            logging.info("沒有更多待處理的評論")
            break

        logging.info(f"處理 {len(reviews)} 則評論...")

        for review_id, content in reviews:
            try:
                logging.info(f"處理評論 ID: {review_id}")

                # 使用 LLM 提取食物項目
                items = extract_food_items_with_llm(content)

                if items:
                    # 儲存提取的項目
                    if save_extracted_items(review_id, items):
                        total_extracted += len(items)
                    else:
                        logging.error(f"評論 {review_id} 儲存失敗")
                        continue
                else:
                    # 沒有提取到項目，僅標記為已處理
                    if not mark_as_processed_only(review_id):
                        logging.error(f"評論 {review_id} 標記失敗")
                        continue

                total_processed += 1

                # API 呼叫間隔 - 遵守免費版限制 (15 requests/minute)
                time.sleep(5)

            except Exception as e:
                logging.error(f"處理評論 {review_id} 時發生錯誤: {e}")
                continue

    logging.info(f"處理完成！總共處理 {total_processed} 則評論，提取 {total_extracted} 個食物項目")

if __name__ == "__main__":
    main()