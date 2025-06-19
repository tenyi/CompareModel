# main.py
import argparse, logging, json, sys
try:
    from config import (OLLAMA_API_BASE_URL, OLLAMA_MODELS_TO_COMPARE, OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY, REVIEWER_MODELS, SUPPORTED_TASKS)
    from ollama_client import OllamaClient
    from reviewer_client import OpenAIReviewerClient, GeminiReviewerClient, DeepSeekReviewerClient
    from reporter import generate_report
except ImportError as e: print(f"Import error in main.py: {e}."); sys.exit(1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_input_text(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: logging.error(f"Error reading file {file_path}: {e}"); raise


def main():
    parser = argparse.ArgumentParser(description="Compare local Ollama LLMs with mock components.")
    parser.add_argument("--input_file", type=str, required=True, help="Input text file path.")
    parser.add_argument("--task", type=str, required=True, choices=SUPPORTED_TASKS.keys(), help="Task type.")
    parser.add_argument("--output_report", type=str, default="comparison_report.md", help="Path to save the markdown report.")
    args = parser.parse_args()
    logging.info(f"Starting task: {SUPPORTED_TASKS.get(args.task, args.task)}, File: {args.input_file}, Report: {args.output_report}")
    try: input_text = load_input_text(args.input_file)
    except: logging.error("Failed to load input file, exiting."); sys.exit(1)


    ollama_client = OllamaClient(host=OLLAMA_API_BASE_URL)
    reviewers = []
    if REVIEWER_MODELS.get("gpt"):
        reviewers.append(OpenAIReviewerClient(api_key=OPENAI_API_KEY, model_name=REVIEWER_MODELS["gpt"]))
    if REVIEWER_MODELS.get("gemini"):
        reviewers.append(GeminiReviewerClient(api_key=GOOGLE_API_KEY, model_name=REVIEWER_MODELS["gemini"]))
    if REVIEWER_MODELS.get("deepseek"):
        reviewers.append(DeepSeekReviewerClient(api_key=DEEPSEEK_API_KEY, model_name=REVIEWER_MODELS["deepseek"]))


    active_reviewers = [r for r in reviewers if r.initialized_successfully]
    logging.info(f"Initialized reviewers (active for evaluation): {[r.model_name for r in active_reviewers]}")
    inactive_reviewers = [r.model_name for r in reviewers if not r.initialized_successfully]
    if inactive_reviewers: logging.info(f"Inactive reviewers (due to placeholder keys, etc.): {inactive_reviewers}")


    all_results = []
    for ollama_model_name in OLLAMA_MODELS_TO_COMPARE:
        logging.info(f"--- Processing Ollama model: {ollama_model_name} ---")
        input_snippet_for_report = input_text[:200] + "..." if len(input_text) > 200 else input_text
        model_result = {"ollama_model": ollama_model_name, "task": args.task, "input_text_snippet": input_snippet_for_report, "ollama_output": "<not_run>", "reviews": []}
        try:
            ollama_output = ollama_client.generate(ollama_model_name, input_text, args.task)
            model_result["ollama_output"] = ollama_output
            logging.info(f"Ollama model ({ollama_model_name}) mock output generated.")
            for reviewer in active_reviewers:
                logging.info(f"Evaluating with mock reviewer {reviewer.model_name}...")
                try:
                    review_data = reviewer.evaluate(input_text, ollama_output, args.task)
                    model_result["reviews"].append({"reviewer_model": reviewer.model_name, "evaluation": review_data})
                except Exception as e: logging.error(f"Mock reviewer {reviewer.model_name} error: {e}")
        except Exception as e: model_result["ollama_output"] = {"error": str(e)}; logging.error(f"Mock Ollama model {ollama_model_name} error: {e}")
        all_results.append(model_result)


    logging.info("--- All models processed (mock) ---")
    try:
        generate_report(all_results, args.output_report)
        logging.info(f"Comparison report (from mock data) saved to: {args.output_report}")
    except Exception as e:
        logging.error(f"Failed to generate report from mock data: {e}")
        print(json.dumps(all_results, indent=4, ensure_ascii=False))


if __name__ == "__main__": main()
