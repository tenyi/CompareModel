# reviewer_client.py
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class BaseReviewerClient:
    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        self.initialized_successfully = False
class OpenAIReviewerClient(BaseReviewerClient):
    def __init__(self, api_key, model_name):
        super().__init__(api_key, model_name)
        if api_key and "YOUR_OPENAI_API_KEY" not in api_key:
            self.initialized_successfully = True
            logging.info(f"MockOpenAIReviewerClient ({model_name}) initialized (API key found).")
        else:
            logging.info(f"MockOpenAIReviewerClient ({model_name}) not initialized (API key is placeholder).")
    def evaluate(self, original_text, ollama_output, task_type):
        if not self.initialized_successfully: return {'error': 'OpenAI client not initialized or API key missing.'}
        logging.info(f"MockOpenAIReviewerClient.evaluate called for {self.model_name}")
        return {'overall_score': 4.5, 'comment': f'Mock OpenAI review for {task_type}: {ollama_output[:20]}...'}
class GeminiReviewerClient(BaseReviewerClient):
    def __init__(self, api_key, model_name):
        super().__init__(api_key, model_name)
        if api_key and "YOUR_GOOGLE_API_KEY" not in api_key:
            self.initialized_successfully = True
            logging.info(f"MockGeminiReviewerClient ({model_name}) initialized (API key found).")
        else:
            self.initialized_successfully = False
            logging.info(f"MockGeminiReviewerClient ({model_name}) not initialized (API key is placeholder).")
    def evaluate(self, original_text, ollama_output, task_type):
        if not self.initialized_successfully: return {'error': 'Gemini client not initialized due to placeholder API key.'}
        logging.info(f"MockGeminiReviewerClient.evaluate called for {self.model_name}")
        return {'overall_score': 4.2, 'comment': f'Mock Gemini review for {task_type}: {ollama_output[:20]}...'}
class DeepSeekReviewerClient(BaseReviewerClient):
    def __init__(self, api_key, model_name):
        super().__init__(api_key, model_name)
        self.initialized_successfully = True
        logging.info(f"MockDeepSeekReviewerClient ({model_name}) initialized (always active for mock).")
    def evaluate(self, original_text, ollama_output, task_type):
        logging.info(f"MockDeepSeekReviewerClient.evaluate called for {self.model_name}")
        return {'overall_score': 3.8, 'comment': f'Mock DeepSeek review for {task_type}: {ollama_output[:20]}...'}
