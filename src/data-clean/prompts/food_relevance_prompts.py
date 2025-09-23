"""
食物相關性判別 Prompt 模組

提供判別評論是否與食物相關的 prompt 模板
"""

from .base_prompts import COMMON_INSTRUCTIONS, format_batch_prompt

# 食物相關性判別的標準
FOOD_RELEVANCE_CRITERIA = """
如果提到食物、菜品、口味、價格、份量等，回答 "Yes"
如果只談論環境、設施、管理、服務等，回答 "No"
"""

def get_food_relevance_batch_prompt(review_batch):
    """取得食物相關性批次判別 prompt"""
    template = """{batch_intro}是否與食物相關，{yes_no_format}

{criteria}

{review_list}

{response_format}
{answer_format}"""

    return format_batch_prompt(
        template,
        review_batch,
        batch_intro=COMMON_INSTRUCTIONS['batch_intro'],
        yes_no_format=COMMON_INSTRUCTIONS['yes_no_format'],
        criteria=FOOD_RELEVANCE_CRITERIA.strip(),
        response_format=COMMON_INSTRUCTIONS['response_format']
    )

def get_food_relevance_single_prompt(content):
    """取得食物相關性單則判別 prompt"""
    return f"""{COMMON_INSTRUCTIONS['single_intro']}是否與食物相關。
{FOOD_RELEVANCE_CRITERIA}

評論：「{content}」

回答："""

# Prompt 版本資訊
PROMPT_VERSION = {
    'version': '1.0',
    'last_updated': '2025-09-23',
    'description': '基礎食物相關性判別 prompt',
    'criteria': [
        '提到食物、菜品、口味、價格、份量 -> Yes',
        '只談論環境、設施、管理、服務 -> No'
    ]
}

def get_prompt_info():
    """取得 prompt 版本資訊"""
    return PROMPT_VERSION