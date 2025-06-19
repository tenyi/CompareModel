# ollama_client.py
import ollama
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class OllamaClient:
    def __init__(self, host=None):
        self.client = ollama.Client(host=host)
        logging.info(f"Ollama Client initialized, host: {host if host else 'default'}")
    def generate(self, model_name: str, input_text: str, task_type: str) -> str:
        prompt = ""
        if task_type == "translate":
            prompt = f"Translate the following English text to Traditional Chinese:\n\n{input_text}"
        elif task_type == "summarize":
            prompt = f"Summarize the following article in Traditional Chinese:\n\n{input_text}"
        else:
            raise ValueError(f"Unsupported task: {task_type}")
        logging.info(f"Sending request to Ollama model {model_name} for task {task_type}...")
        try:
            response = self.client.generate(model=model_name, prompt=prompt)
            if 'response' in response and response['response'].strip():
                return response['response'].strip()
            raise RuntimeError(f"Ollama model {model_name} bad response: {response}")
        except ollama.ResponseError as e:
            err_msg = str(e.error) if e.error else ""
            if "model not found" in err_msg.lower():
                raise RuntimeError(f"Ollama model {model_name} not found. Error: {e.error}")
            raise RuntimeError(f"Ollama API error (model: {model_name}): {e.error}")
        except Exception as e:
            raise RuntimeError(f"Error calling Ollama model {model_name}: {e}")
