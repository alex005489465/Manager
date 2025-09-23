"""
具體食物項目判別 Prompt 模組

提供判別評論是否提到具體食物項目或店家的 prompt 模板
"""

from .base_prompts import COMMON_INSTRUCTIONS, format_batch_prompt

# 具體食物項目判別的標準
SPECIFIC_FOOD_CRITERIA = """
判別標準：
- 具體提及：特定料理名稱、店家名稱、攤位描述、特定食材或口味描述
- 泛指評論：只提到「好吃」、「便宜」、「不錯」等一般性描述

如果有具體提及，回答 "Yes"
如果只是泛指，回答 "No"
"""

# 具體食物項目的範例
SPECIFIC_FOOD_EXAMPLES = """
具體提及範例：
✅ 牛肉麵、臭豆腐、雞排、大腸包小腸
✅ 第三排第五攤、轉角那家、阿婆的攤子
✅ 麻辣、清淡、酸甜、香脆
✅ 豬血糕、花枝丸、蔥抓餅

泛指範例：
❌ 好吃、便宜、不錯、還可以
❌ 食物、東西、小吃
❌ 划算、貴、值得
"""

def get_specific_food_batch_prompt(review_batch, include_examples=True):
    """取得具體食物項目批次判別 prompt"""
    template = """{batch_intro}是否提到具體的食物項目或店家。

{criteria}

{examples}

{review_list}

{response_format}
{answer_format}"""

    examples_text = SPECIFIC_FOOD_EXAMPLES if include_examples else ""

    return format_batch_prompt(
        template,
        review_batch,
        batch_intro=COMMON_INSTRUCTIONS['batch_intro'],
        criteria=SPECIFIC_FOOD_CRITERIA.strip(),
        examples=examples_text.strip(),
        response_format=COMMON_INSTRUCTIONS['response_format']
    )

def get_specific_food_single_prompt(content, include_examples=True):
    """取得具體食物項目單則判別 prompt"""
    examples_text = f"\n\n{SPECIFIC_FOOD_EXAMPLES}" if include_examples else ""

    return f"""{COMMON_INSTRUCTIONS['single_intro']}是否提到具體的食物項目或店家。

{SPECIFIC_FOOD_CRITERIA.strip()}{examples_text}

評論：「{content}」

回答："""

def get_simplified_specific_food_prompt(review_batch):
    """取得簡化版的具體食物項目 prompt（不含範例）"""
    return get_specific_food_batch_prompt(review_batch, include_examples=False)

# Prompt 版本資訊
PROMPT_VERSION = {
    'version': '1.0',
    'last_updated': '2025-09-23',
    'description': '具體食物項目判別 prompt',
    'criteria': [
        '具體提及：特定料理名稱、店家名稱、攤位描述、特定食材或口味描述 -> Yes',
        '泛指評論：只提到好吃、便宜、不錯等一般性描述 -> No'
    ],
    'examples_included': True
}

def get_prompt_info():
    """取得 prompt 版本資訊"""
    return PROMPT_VERSION

# 可調整的設定
PROMPT_SETTINGS = {
    'include_examples_by_default': True,
    'use_traditional_chinese': True,
    'detailed_criteria': True
}

def update_prompt_settings(**kwargs):
    """更新 prompt 設定"""
    PROMPT_SETTINGS.update(kwargs)

def get_prompt_settings():
    """取得目前的 prompt 設定"""
    return PROMPT_SETTINGS.copy()