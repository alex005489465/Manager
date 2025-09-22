#!/usr/bin/env python
"""
測試收集一頁 Google Maps 評論
"""

from data_collection.google_reviews_collector import GoogleReviewsCollector
from data_collection.config import config

def test_one_page():
    """測試收集一頁評論"""
    print("開始測試收集一頁評論...")
    print(f"目標地點: {config.TARGET_LOCATION}")
    print(f"Data ID: {config.TARGET_LOCATION_ID}")
    print(f"API 金鑰: {config.SERP_API_KEY[:10]}...")

    # 初始化收集器
    collector = GoogleReviewsCollector()

    # 收集一頁評論
    place_id = config.TARGET_LOCATION_ID
    stats = collector.collect_reviews(
        place_id=place_id,
        start_page=1,
        max_pages=2  # 收集兩頁測試分頁功能
    )

    print("\n收集結果:")
    print(f"總請求頁數: {stats['total_pages_requested']}")
    print(f"成功頁數: {stats['successful_pages']}")
    print(f"失敗頁數: {stats['failed_pages']}")
    print(f"總評論數: {stats['total_reviews_collected']}")
    print(f"保存文件: {stats['saved_files']}")

    return stats

if __name__ == "__main__":
    try:
        result = test_one_page()
        if result['successful_pages'] > 0:
            print("測試成功！")
        else:
            print("測試失敗！")
    except Exception as e:
        print(f"測試異常: {e}")
        import traceback
        traceback.print_exc()