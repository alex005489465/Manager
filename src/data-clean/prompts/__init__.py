"""
Prompts 模組 - 管理所有 AI 分析用的 Prompt 模板

此模組包含：
- food_relevance_prompts: 食物相關性判別 prompt
- specific_food_prompts: 具體食物項目判別 prompt
- base_prompts: 共用的 prompt 元素和工具函數

使用範例:
    from prompts.food_relevance_prompts import get_food_relevance_batch_prompt
    from prompts.specific_food_prompts import get_specific_food_batch_prompt
"""

from .food_relevance_prompts import (
    get_food_relevance_batch_prompt,
    get_food_relevance_single_prompt
)

from .specific_food_prompts import (
    get_specific_food_batch_prompt,
    get_specific_food_single_prompt
)

from .base_prompts import (
    format_batch_prompt,
    format_answer_format,
    create_review_list
)

__all__ = [
    'get_food_relevance_batch_prompt',
    'get_food_relevance_single_prompt',
    'get_specific_food_batch_prompt',
    'get_specific_food_single_prompt',
    'format_batch_prompt',
    'format_answer_format',
    'create_review_list'
]