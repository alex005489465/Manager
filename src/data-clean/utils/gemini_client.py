"""
Gemini API 客戶端工具

提供 Gemini API 的封裝和管理功能
"""

import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
from prompts.base_prompts import parse_batch_response, validate_batch_response

class GeminiClient:
    """Gemini API 客戶端管理類別"""

    def __init__(self, model_name='gemini-2.5-flash-lite', auto_load_env=True):
        """
        初始化 Gemini 客戶端

        Args:
            model_name (str): 使用的 Gemini 模型名稱
            auto_load_env (bool): 是否自動載入環境變數
        """
        if auto_load_env:
            load_dotenv()

        self.model_name = model_name
        self.model = None
        self._setup_api()

    def _setup_api(self):
        """設定 Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("請在 .env 檔案中設定 GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt):
        """
        生成內容

        Args:
            prompt (str): 輸入的 prompt

        Returns:
            str: API 回應的文字內容
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API 呼叫錯誤: {e}")

    def analyze_single(self, prompt):
        """
        分析單則內容

        Args:
            prompt (str): 分析用的 prompt

        Returns:
            bool or None: True/False 的分析結果，或 None 表示解析失敗
        """
        try:
            result = self.generate_content(prompt)

            # 解析單則回應
            if 'Yes' in result or 'yes' in result or 'YES' in result:
                return True
            elif 'No' in result or 'no' in result or 'NO' in result:
                return False
            else:
                print(f"無法解析的單則回應: {result}")
                return None

        except Exception as e:
            print(f"單則分析錯誤: {e}")
            return None

    def analyze_batch(self, prompt, expected_count):
        """
        批次分析內容

        Args:
            prompt (str): 批次分析用的 prompt
            expected_count (int): 預期的回應數量

        Returns:
            list or None: 布林值列表，或 None 表示批次分析失敗
        """
        try:
            result = self.generate_content(prompt)

            # 驗證回應格式
            is_valid, message = validate_batch_response(result, expected_count)
            if not is_valid:
                print(f"批次回應格式錯誤: {message}")
                print(f"原始回應: {result}")
                return None

            # 解析批次回應
            results = parse_batch_response(result, expected_count)

            # 檢查結果數量
            if len(results) != expected_count:
                print(f"批次結果數量不符: 預期 {expected_count}，得到 {len(results)}")
                return None

            return results

        except Exception as e:
            print(f"批次分析錯誤: {e}")
            return None

    def get_model_info(self):
        """取得模型資訊"""
        return {
            'model_name': self.model_name,
            'api_configured': self.model is not None
        }

class RateLimitedGeminiClient(GeminiClient):
    """帶有速率限制的 Gemini 客戶端"""

    def __init__(self, model_name='gemini-2.5-flash-lite',
                 requests_per_minute=15, auto_load_env=True):
        """
        初始化帶速率限制的客戶端

        Args:
            model_name (str): 使用的 Gemini 模型名稱
            requests_per_minute (int): 每分鐘最大請求數
            auto_load_env (bool): 是否自動載入環境變數
        """
        super().__init__(model_name, auto_load_env)
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0

    def _wait_if_needed(self):
        """如需要則等待以遵守速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def generate_content(self, prompt):
        """帶速率限制的內容生成"""
        self._wait_if_needed()
        return super().generate_content(prompt)

    def analyze_single(self, prompt):
        """帶速率限制的單則分析"""
        self._wait_if_needed()
        return super().analyze_single(prompt)

    def analyze_batch(self, prompt, expected_count):
        """帶速率限制的批次分析"""
        self._wait_if_needed()
        return super().analyze_batch(prompt, expected_count)

# 工廠函數
def create_gemini_client(use_rate_limit=True, **kwargs):
    """
    建立 Gemini 客戶端

    Args:
        use_rate_limit (bool): 是否使用速率限制
        **kwargs: 傳遞給客戶端的其他參數

    Returns:
        GeminiClient: Gemini 客戶端實例
    """
    if use_rate_limit:
        return RateLimitedGeminiClient(**kwargs)
    else:
        return GeminiClient(**kwargs)