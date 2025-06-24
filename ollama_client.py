# ollama_client.py
# 此檔案包含用於與 Ollama 大型語言模型互動的客戶端。
# 注意：目前這是一個模擬 (Mock) 的客戶端，用於測試和開發目的。

import logging # 用於記錄程式運行訊息

# 設定日誌記錄的基本配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OllamaClient:
    """
    Ollama 客戶端類別。
    用於與 Ollama 服務互動，以產生文字或執行其他相關任務。
    這是一個模擬客戶端，其行為是預先定義的，而不是實際呼叫 Ollama API。
    """
    def __init__(self, host=None):
        """
        初始化 OllamaClient。

        Args:
            host (str, optional): Ollama 服務的主機位址。預設為 None。
                                  在模擬客戶端中，此參數主要用於記錄。
        """
        # 記錄客戶端初始化，並註明主機資訊
        logging.info(f"MockOllamaClient initialized for host: {host}")

    def generate(self, model_name: str, input_text: str, task_type: str) -> str:
        """
        使用指定的 Ollama 模型根據輸入文字和任務類型產生輸出。
        這是一個模擬方法。

        Args:
            model_name (str): 要使用的 Ollama 模型名稱 (例如 "llama2:7b")。
            input_text (str): 提供給模型的輸入文字。
            task_type (str): 任務的類型 (例如 "summarize", "translate")。

        Returns:
            str: 模型產生的模擬輸出文字。

        Raises:
            RuntimeError: 如果模型名稱是 "another-mock-model:13b"，則模擬錯誤。
        """
        # 記錄 generate 方法的呼叫，包含模型名稱和任務類型
        logging.info(
            f"MockOllamaClient.generate called for model: {model_name}, task: {task_type}"
        )
        # 模擬特定模型的錯誤情況
        if model_name == "another-mock-model:13b":
            raise RuntimeError(f"Simulated error for Ollama model {model_name}")
        # 回傳一個模擬的成功輸出
        return f"Simulated successful output from {model_name} for task {task_type} on input: '{input_text[:30]}...'"
