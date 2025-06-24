# ollama_client.py
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OllamaClient:
    def __init__(self, host=None):
        logging.info(f"MockOllamaClient initialized for host: {host}")

    def generate(self, model_name: str, input_text: str, task_type: str) -> str:
        logging.info(
            f"MockOllamaClient.generate called for model: {model_name}, task: {task_type}"
        )
        if model_name == "another-mock-model:13b":
            raise RuntimeError(f"Simulated error for Ollama model {model_name}")
        return f"Simulated successful output from {model_name} for task {task_type} on input: '{input_text[:30]}...'"
