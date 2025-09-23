#!/usr/bin/env python3
"""
具體食物項目分析腳本（重構版本）

使用新的模組化架構分析食物相關評論中是否提到具體的食物項目或店家

依賴：
- utils.gemini_client: Gemini API 客戶端
- utils.database_manager: 資料庫管理
- utils.prompt_loader: Prompt 載入
- prompts.specific_food_prompts: 具體食物項目 prompt
"""

import time
from utils.gemini_client import create_gemini_client
from utils.database_manager import ReviewAnalysisManager
from utils.prompt_loader import create_prompt_loader, validate_prompt_input

# 處理設定
BATCH_SIZE = 15
BATCH_DELAY = 5  # 批次間延遲秒數

def process_batch(client, db_manager, prompt_loader, batch, batch_num, total_batches):
    """處理單一批次的評論"""
    print(f"\n處理第 {batch_num}/{total_batches} 批次 ({len(batch)} 則評論)")

    # 驗證批次輸入
    is_valid, message = validate_prompt_input(review_batch=batch)
    if not is_valid:
        print(f"批次輸入驗證失敗: {message}")
        return None

    # 取得批次 prompt
    try:
        prompt = prompt_loader.get_specific_food_prompt(review_batch=batch)
        batch_results = client.analyze_batch(prompt, len(batch))

        if batch_results is not None:
            return batch_results
        else:
            print(f"批次 {batch_num} API 分析失敗")
            return None

    except Exception as e:
        print(f"批次 {batch_num} 處理錯誤: {e}")
        return None

def process_single_fallback(client, db_manager, prompt_loader, batch, batch_num):
    """單則處理的回退方案"""
    print(f"批次 {batch_num} 回退到逐則處理")

    results = []
    for review_id, content in batch:
        print(f"  處理評論 ID: {review_id}")

        try:
            prompt = prompt_loader.get_specific_food_prompt(content=content)
            result = client.analyze_single(prompt)
            results.append(result)
            time.sleep(2)  # 較短的延遲
        except Exception as e:
            print(f"  評論 ID {review_id} 處理失敗: {e}")
            results.append(None)

    return results

def update_database_batch(db_manager, batch, results):
    """批次更新資料庫"""
    updates = []
    stats = {'processed': 0, 'specific_food': 0, 'general_food': 0, 'failed': 0}

    for (review_id, content), result in zip(batch, results):
        if result is not None:
            updates.append((result, review_id))
            stats['processed'] += 1
            if result:
                stats['specific_food'] += 1
            else:
                stats['general_food'] += 1
        else:
            stats['failed'] += 1

    if updates:
        db_manager.batch_update_specific_food_mention(updates)

    return stats

def process_specific_food_analysis():
    """主要處理流程（重構版本）"""
    print("=== 具體食物項目分析處理 ===")

    # 初始化元件
    try:
        client = create_gemini_client(use_rate_limit=True, requests_per_minute=15)
        db_manager = ReviewAnalysisManager()
        prompt_loader = create_prompt_loader()
        print("系統元件初始化完成")
    except Exception as e:
        print(f"系統初始化失敗: {e}")
        return

    # 取得待處理的食物相關評論
    try:
        reviews = db_manager.get_food_related_reviews()
        total_reviews = len(reviews)
        print(f"找到 {total_reviews} 則需要處理的食物相關評論")

        if total_reviews == 0:
            print("沒有需要處理的食物相關評論")
            return
    except Exception as e:
        print(f"取得評論資料失敗: {e}")
        return

    # 批次處理
    total_stats = {'processed': 0, 'specific_food': 0, 'general_food': 0, 'failed': 0}

    for i in range(0, total_reviews, BATCH_SIZE):
        batch = reviews[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total_reviews + BATCH_SIZE - 1) // BATCH_SIZE

        # 嘗試批次處理
        batch_results = process_batch(client, db_manager, prompt_loader, batch, batch_num, total_batches)

        # 如果批次處理失敗，回退到逐則處理
        if batch_results is None:
            batch_results = process_single_fallback(client, db_manager, prompt_loader, batch, batch_num)

        # 更新資料庫
        if batch_results:
            try:
                batch_stats = update_database_batch(db_manager, batch, batch_results)

                # 累計統計
                for key in total_stats:
                    total_stats[key] += batch_stats[key]

                print(f"批次 {batch_num} 完成 - 處理: {batch_stats['processed']}, 失敗: {batch_stats['failed']}")

                # 批次間延遲
                if batch_num < total_batches:
                    time.sleep(BATCH_DELAY)

            except Exception as e:
                print(f"批次 {batch_num} 資料庫更新失敗: {e}")

    # 顯示最終統計
    print(f"\n=== 處理完成 ===")
    print(f"總共處理: {total_stats['processed']} 則評論")
    print(f"具體食物提及: {total_stats['specific_food']} 則")
    print(f"泛指食物評論: {total_stats['general_food']} 則")
    print(f"處理失敗: {total_stats['failed']} 則")

    # 顯示資料庫統計
    try:
        db_stats = db_manager.get_analysis_statistics()
        print(f"\n=== 資料庫統計 ===")
        print(f"總評論數: {db_stats['total_reviews']}")

        print(f"\n食物相關性分布:")
        for status, count in db_stats['food_relevance_stats']:
            if status is None:
                print(f"  未處理: {count} 則")
            elif status:
                print(f"  食物相關: {count} 則")
            else:
                print(f"  非食物相關: {count} 則")

        print(f"\n具體食物提及分布:")
        for status, count in db_stats['specific_food_stats']:
            if status is None:
                print(f"  未判別: {count} 則")
            elif status:
                print(f"  具體提及: {count} 則")
            else:
                print(f"  泛指評論: {count} 則")

    except Exception as e:
        print(f"取得統計資訊失敗: {e}")

    # 顯示 prompt 使用統計
    try:
        usage_stats = prompt_loader.get_usage_stats()
        print(f"\n=== Prompt 使用統計 ===")
        print(f"批次呼叫: {usage_stats['usage_stats']['specific_food']['batch']} 次")
        print(f"單則呼叫: {usage_stats['usage_stats']['specific_food']['single']} 次")
    except Exception as e:
        print(f"取得 Prompt 統計失敗: {e}")

def generate_analysis_report():
    """生成詳細的分析結果報告"""
    try:
        db_manager = ReviewAnalysisManager()

        # 取得樣本評論
        specific_samples = db_manager.get_sample_reviews('specific_food', 5)
        general_samples = db_manager.get_sample_reviews('general_food', 5)

        print(f"\n=== 樣本評論 ===")
        print(f"\n具體食物提及範例:")
        for i, (review_id, preview) in enumerate(specific_samples, 1):
            print(f"  {i}. (ID:{review_id}) {preview}...")

        print(f"\n泛指食物評論範例:")
        for i, (review_id, preview) in enumerate(general_samples, 1):
            print(f"  {i}. (ID:{review_id}) {preview}...")

    except Exception as e:
        print(f"生成報告失敗: {e}")

if __name__ == "__main__":
    print("=== 具體食物項目分析工具 ===")
    print("分析食物相關評論中是否提到具體的食物項目或店家")
    print()

    try:
        process_specific_food_analysis()
        generate_analysis_report()
    except KeyboardInterrupt:
        print("\n使用者中斷處理")
    except Exception as e:
        print(f"執行錯誤: {e}")