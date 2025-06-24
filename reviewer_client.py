# reviewer_client.py
# 此檔案包含用於評估 Ollama 模型輸出的各種評審客戶端。
# 注意：目前這些都是模擬 (Mock) 的客戶端，用於測試和開發目的。

import logging # 用於記錄程式運行訊息

# 設定日誌記錄的基本配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BaseReviewerClient:
    """
    評審客戶端的基礎類別。
    定義了所有評審客戶端共有的屬性和方法。
    """
    def __init__(self, api_key, model_name):
        """
        初始化基礎評審客戶端。

        Args:
            api_key (str): 用於存取評審服務的 API 金鑰。
            model_name (str): 評審模型的名稱。
        """
        self.api_key = api_key # API 金鑰
        self.model_name = model_name # 評審模型名稱
        # initialized_successfully: 標記客戶端是否成功初始化 (例如，API 金鑰是否有效)
        self.initialized_successfully = False


class OpenAIReviewerClient(BaseReviewerClient):
    """
    使用 OpenAI 模型進行評審的客戶端。
    這是一個模擬客戶端。
    """
    def __init__(self, api_key, model_name):
        """
        初始化 OpenAI 評審客戶端。

        Args:
            api_key (str): OpenAI API 金鑰。
            model_name (str): OpenAI 模型的名稱。
        """
        super().__init__(api_key, model_name) # 呼叫基礎類別的初始化方法
        # 檢查 API 金鑰是否提供且不是預留位置
        if api_key and "YOUR_OPENAI_API_KEY" not in api_key:
            self.initialized_successfully = True # 標記為成功初始化
            logging.info(
                f"MockOpenAIReviewerClient ({model_name}) initialized (API key found)."
            )
        else:
            # 如果 API 金鑰缺失或為預留位置，則記錄未初始化
            logging.info(
                f"MockOpenAIReviewerClient ({model_name}) not initialized (API key is placeholder)."
            )

    def evaluate(self, original_text, ollama_output, task_type):
        """
        使用 OpenAI 模型評估 Ollama 模型的輸出。
        這是一個模擬方法。

        Args:
            original_text (str): 原始輸入文字。
            ollama_output (str): Ollama 模型的輸出文字。
            task_type (str): 執行的任務類型 (例如 "summarize", "translate")。

        Returns:
            dict: 包含評估結果的字典，例如評分和評論。
                  如果客戶端未成功初始化，則回傳錯誤訊息。
        """
        # 如果客戶端未成功初始化，則回傳錯誤
        if not self.initialized_successfully:
            return {"error": "OpenAI client not initialized or API key missing."}
        # 記錄評估方法的呼叫
        logging.info(f"MockOpenAIReviewerClient.evaluate called for {self.model_name}")
        # 回傳模擬的評估結果
        return {
            "overall_score": 4.5, # 模擬的總體評分
            "comment": f"Mock OpenAI review for {task_type}: {ollama_output[:20]}...", # 模擬的評論
        }


class GeminiReviewerClient(BaseReviewerClient):
    """
    使用 Google Gemini 模型進行評審的客戶端。
    這是一個模擬客戶端。
    """
    def __init__(self, api_key, model_name):
        """
        初始化 Gemini 評審客戶端。

        Args:
            api_key (str): Google API 金鑰。
            model_name (str): Gemini 模型的名稱。
        """
        super().__init__(api_key, model_name) # 呼叫基礎類別的初始化方法
        # 檢查 API 金鑰是否提供且不是預留位置
        if api_key and "YOUR_GOOGLE_API_KEY" not in api_key:
            self.initialized_successfully = True # 標記為成功初始化
            logging.info(
                f"MockGeminiReviewerClient ({model_name}) initialized (API key found)."
            )
        else:
            self.initialized_successfully = False # 標記為未成功初始化
            logging.info(
                f"MockGeminiReviewerClient ({model_name}) not initialized (API key is placeholder)."
            )

    def evaluate(self, original_text, ollama_output, task_type):
        """
        使用 Gemini 模型評估 Ollama 模型的輸出。
        這是一個模擬方法。

        Args:
            original_text (str): 原始輸入文字。
            ollama_output (str): Ollama 模型的輸出文字。
            task_type (str): 執行的任務類型。

        Returns:
            dict: 包含評估結果的字典。
                  如果客戶端未成功初始化，則回傳錯誤訊息。
        """
        # 如果客戶端未成功初始化，則回傳錯誤
        if not self.initialized_successfully:
            return {
                "error": "Gemini client not initialized due to placeholder API key."
            }
        # 記錄評估方法的呼叫
        logging.info(f"MockGeminiReviewerClient.evaluate called for {self.model_name}")
        # 回傳模擬的評估結果
        return {
            "overall_score": 4.2, # 模擬的總體評分
            "comment": f"Mock Gemini review for {task_type}: {ollama_output[:20]}...", # 模擬的評論
        }


class DeepSeekReviewerClient(BaseReviewerClient):
    """
    使用 DeepSeek 模型進行評審的客戶端。
    這是一個模擬客戶端，且假設總是成功初始化。
    """
    def __init__(self, api_key, model_name):
        """
        初始化 DeepSeek 評審客戶端。

        Args:
            api_key (str): DeepSeek API 金鑰 (在模擬中未使用，但為保持一致性而保留)。
            model_name (str): DeepSeek 模型的名稱。
        """
        super().__init__(api_key, model_name) # 呼叫基礎類別的初始化方法
        self.initialized_successfully = True # 模擬客戶端總是成功初始化
        logging.info(
            f"MockDeepSeekReviewerClient ({model_name}) initialized (always active for mock)."
        )

    def evaluate(self, original_text, ollama_output, task_type):
        """
        使用 DeepSeek 模型評估 Ollama 模型的輸出。
        這是一個模擬方法。

        Args:
            original_text (str): 原始輸入文字。
            ollama_output (str): Ollama 模型的輸出文字。
            task_type (str): 執行的任務類型。

        Returns:
            dict: 包含評估結果的字典。
        """
        # 記錄評估方法的呼叫
        logging.info(
            f"MockDeepSeekReviewerClient.evaluate called for {self.model_name}"
        )
        # 回傳模擬的評估結果
        return {
            "overall_score": 3.8, # 模擬的總體評分
            "comment": f"Mock DeepSeek review for {task_type}: {ollama_output[:20]}...", # 模擬的評論
        }
