# reviewer_client.py
import logging, json
from abc import ABC, abstractmethod
try:
    from openai import OpenAI
except ImportError: OpenAI = None
try:
    import google.generativeai as genai
except ImportError: genai = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseReviewerClient(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key; self.model_name = model_name
        self.initialized_successfully = False
        if not api_key or "YOUR_API_KEY" in api_key: logging.warning(f"API key for {self.model_name} is placeholder.")
        else: self._setup_client()
    @abstractmethod
    def _setup_client(self): pass
    def _construct_prompt(self, original_text: str, ollama_output: str, task_type: str) -> str:
        if task_type == "translate":
            return f'''Original English Text:\n{original_text}\n\nModel Translation (Traditional Chinese):\n{ollama_output}\n\nEvaluate the translation (1-5, 5 best) for: 1. Accuracy 2. Fluency 3. Correct Traditional Chinese usage. Provide JSON: {{"accuracy_score": 0, "fluency_score": 0, "traditional_chinese_usage_score": 0, "overall_score": 0, "comment": "text"}}'''
        elif task_type == "summarize":
            return f'''Original Article:\n{original_text}\n\nModel Summary (Traditional Chinese):\n{ollama_output}\n\nEvaluate the summary (1-5, 5 best) for: 1. Relevance 2. Completeness 3. Conciseness 4. Language. Provide JSON: {{"relevance_score": 0, "completeness_score": 0, "conciseness_score": 0, "language_expression_score": 0, "overall_score": 0, "comment": "text"}}'''
        raise ValueError(f"Unsupported review task: {task_type}")
    @abstractmethod
    def evaluate(self, original_text: str, ollama_output: str, task_type: str) -> dict: pass
    def _parse_json_response(self, response_text: str, task_type: str) -> dict:
        try:
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("```"):
                response_text = response_text.strip()[3:-3].strip()
            eval_data = json.loads(response_text)
            if not isinstance(eval_data.get("overall_score"), (int, float)) or not isinstance(eval_data.get("comment"), str):
                raise ValueError("Missing overall_score or comment.")
            return eval_data
        except Exception as e:
            return {"error": f"JSON parsing failed: {e}", "raw_response": response_text}


class OpenAIReviewerClient(BaseReviewerClient):
    def _setup_client(self):
        if not OpenAI: logging.error("OpenAI SDK not found."); return
        try: self.client = OpenAI(api_key=self.api_key); self.initialized_successfully = True; logging.info(f"OpenAIReviewerClient ({self.model_name}) initialized.")
        except Exception as e: logging.error(f"OpenAI Client init failed for {self.model_name}: {e}")
    def evaluate(self, original_text: str, ollama_output: str, task_type: str) -> dict:
        if not self.initialized_successfully: return {"error": "OpenAIReviewerClient not initialized"}
        prompt = self._construct_prompt(original_text, ollama_output, task_type)
        try:
            completion = self.client.chat.completions.create(model=self.model_name, messages=[{"role": "system", "content": "Output JSON"}, {"role": "user", "content": prompt}], response_format={"type": "json_object"})
            return self._parse_json_response(completion.choices[0].message.content, task_type)
        except Exception as e: return {"error": f"OpenAI API error: {e}"}


class GeminiReviewerClient(BaseReviewerClient):
    def _setup_client(self):
        if not genai: logging.error("Google GenAI SDK not found."); return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name, generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
            self.initialized_successfully = True; logging.info(f"GeminiReviewerClient ({self.model_name}) initialized.")
        except Exception as e: logging.error(f"Gemini Client init failed for {self.model_name}: {e}")
    def evaluate(self, original_text: str, ollama_output: str, task_type: str) -> dict:
        if not self.initialized_successfully: return {"error": "GeminiReviewerClient not initialized"}
        prompt = self._construct_prompt(original_text, ollama_output, task_type)
        try:
            response = self.model.generate_content(prompt)
            response_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            if not response_text and response.prompt_feedback and response.prompt_feedback.block_reason: return {"error": f"Gemini request blocked: {response.prompt_feedback.block_reason}"}
            return self._parse_json_response(response_text, task_type)
        except Exception as e: return {"error": f"Gemini API error: {e}"}


class DeepSeekReviewerClient(BaseReviewerClient):
    def _setup_client(self):
        if self.api_key and "YOUR_API_KEY" not in self.api_key: logging.info(f"DeepSeekReviewerClient ({self.model_name}) has API key, but is mock.")
        else: logging.info(f"DeepSeekReviewerClient ({self.model_name}) is mock (no API key).")
        self.initialized_successfully = True
    def evaluate(self, original_text: str, ollama_output: str, task_type: str) -> dict:
        logging.info(f"DeepSeekReviewerClient.evaluate ({self.model_name}) mock call.")
        base_scores = {"overall_score": 3.0, "comment": "DeepSeek (mock) evaluation."}
        if task_type == "translate":
            base_scores.update({"accuracy_score":3, "fluency_score":3, "traditional_chinese_usage_score":3})
        elif task_type == "summarize":
            base_scores.update({"relevance_score":3, "completeness_score":3, "conciseness_score":3, "language_expression_score":3})
        return base_scores
