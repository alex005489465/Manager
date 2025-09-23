"""
基礎 Prompt 工具模組

提供共用的 prompt 格式化和建構函數
"""

def create_review_list(review_batch):
    """建立評論列表字串"""
    review_list = ""
    for i, (review_id, content) in enumerate(review_batch, 1):
        review_list += f"評論{i}：「{content}」\n"
    return review_list.strip()

def format_answer_format(review_count):
    """建立回答格式字串"""
    answer_format = ""
    for i in range(1, review_count + 1):
        answer_format += f"{i}. Yes/No\n"
    return answer_format.strip()

def format_batch_prompt(template, review_batch, **kwargs):
    """格式化批次處理 prompt"""
    review_list = create_review_list(review_batch)
    answer_format = format_answer_format(len(review_batch))

    return template.format(
        review_list=review_list,
        answer_format=answer_format,
        **kwargs
    )

def validate_batch_response(response_text, expected_count):
    """驗證 AI 回應格式是否正確"""
    if not response_text:
        return False, "回應為空"

    lines = response_text.strip().split('\n')
    valid_lines = []

    for line in lines:
        line = line.strip()
        if line and any(str(i) in line for i in range(1, expected_count + 1)):
            if 'Yes' in line or 'No' in line:
                valid_lines.append(line)

    if len(valid_lines) != expected_count:
        return False, f"預期 {expected_count} 行回應，實際得到 {len(valid_lines)} 行"

    return True, "格式正確"

def parse_batch_response(response_text, expected_count):
    """解析批次回應為布林值列表"""
    lines = response_text.strip().split('\n')
    results = []

    for i in range(expected_count):
        found = False
        for line in lines:
            line = line.strip()
            if str(i+1) in line or f"{i+1}." in line:
                if 'Yes' in line or 'yes' in line or 'YES' in line:
                    results.append(True)
                    found = True
                    break
                elif 'No' in line or 'no' in line or 'NO' in line:
                    results.append(False)
                    found = True
                    break

        if not found:
            results.append(None)

    return results

# 共用的 prompt 元素
COMMON_INSTRUCTIONS = {
    'response_format': "請按順序回答（只要數字和答案）：",
    'yes_no_format': "對每則評論回答 Yes 或 No。",
    'batch_intro': "請判斷以下夜市評論",
    'single_intro': "請判斷以下夜市評論"
}

# 評論品質檢查
def validate_review_content(content):
    """檢查評論內容是否適合分析"""
    if not content or not content.strip():
        return False, "評論內容為空"

    if len(content.strip()) < 3:
        return False, "評論內容過短"

    return True, "評論內容有效"