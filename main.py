# main.py
# 主要的程式進入點，用於比較本地 Ollama 大型語言模型與模擬組件。

# 匯入必要的模組
import argparse  # 用於解析命令列參數
import logging  # 用於記錄程式運行訊息
import json  # 用於處理 JSON 格式的資料
import sys  # 用於存取系統相關的參數和函數

# 嘗試從 config 模組匯入設定，以及從其他自訂模組匯入類別
try:
    from config import (
        OLLAMA_API_BASE_URL,  # Ollama API 的基礎 URL
        OLLAMA_MODELS_TO_COMPARE,  # 要比較的 Ollama 模型列表
        OPENAI_API_KEY,  # OpenAI API 金鑰
        GOOGLE_API_KEY,  # Google API 金鑰
        DEEPSEEK_API_KEY,  # DeepSeek API 金鑰
        REVIEWER_MODELS,  # 評審模型的設定
        SUPPORTED_TASKS,  # 支援的任務類型
    )
    from ollama_client import OllamaClient  # Ollama 客戶端，用於與 Ollama 模型互動
    from reviewer_client import (  # 評審客戶端，用於不同模型的評審
        OpenAIReviewerClient,
        GeminiReviewerClient,
        DeepSeekReviewerClient,
    )
    from reporter import generate_report  # 報告產生器，用於產生比較報告
except ImportError as e:
    # 如果匯入失敗，則印出錯誤訊息並結束程式
    print(f"Import error in main.py: {e}.")
    sys.exit(1)

# 設定日誌記錄的基本配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_input_text(file_path: str) -> str:
    """
    從指定的檔案路徑載入輸入文字。

    Args:
        file_path (str): 輸入文字檔案的路徑。

    Returns:
        str: 檔案的內容。

    Raises:
        Exception: 如果讀取檔案時發生錯誤。
    """
    try:
        # 開啟並讀取檔案內容
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # 如果發生錯誤，記錄錯誤訊息並重新引發例外
        logging.error(f"Error reading file {file_path}: {e}")
        raise


def main():
    """
    主要的執行函數。
    解析命令列參數，載入輸入，初始化客戶端，處理模型，並產生報告。
    """
    # 建立命令列參數解析器
    parser = argparse.ArgumentParser(
        description="Compare local Ollama LLMs with mock components."
    )
    # 新增 --input_file 參數，用於指定輸入文字檔案的路徑
    parser.add_argument(
        "--input_file", type=str, required=True, help="Input text file path."
    )
    # 新增 --task 參數，用於指定任務類型
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        choices=SUPPORTED_TASKS.keys(),  # 任務類型的選項來自 SUPPORTED_TASKS
        help="Task type.",
    )
    # 新增 --output_report 參數，用於指定輸出報告的路徑
    parser.add_argument(
        "--output_report",
        type=str,
        default="comparison_report.md",  # 預設報告名稱
        help="Path to save the markdown report.",
    )
    # 解析命令列參數
    args = parser.parse_args()

    # 記錄開始執行的任務資訊
    logging.info(
        f"Starting task: {SUPPORTED_TASKS.get(args.task, args.task)}, File: {args.input_file}, Report: {args.output_report}"
    )

    # 載入輸入文字
    try:
        input_text = load_input_text(args.input_file)  # 從指定檔案載入文字
    except:
        # 如果載入失敗，記錄錯誤訊息並結束程式
        logging.error("Failed to load input file, exiting.")
        sys.exit(1)

    # 初始化 Ollama 客戶端
    ollama_client = OllamaClient(host=OLLAMA_API_BASE_URL)

    # 初始化評審客戶端列表
    reviewers = []  # 儲存所有評審客戶端實例的列表
    # 根據設定檔中的 REVIEWER_MODELS 初始化不同的評審客戶端
    if REVIEWER_MODELS.get("gpt"):
        reviewers.append(
            OpenAIReviewerClient(
                api_key=OPENAI_API_KEY, model_name=REVIEWER_MODELS["gpt"]
            )
        )
    if REVIEWER_MODELS.get("gemini"):
        reviewers.append(
            GeminiReviewerClient(
                api_key=GOOGLE_API_KEY, model_name=REVIEWER_MODELS["gemini"]
            )
        )
    if REVIEWER_MODELS.get("deepseek"):
        reviewers.append(
            DeepSeekReviewerClient(
                api_key=DEEPSEEK_API_KEY, model_name=REVIEWER_MODELS["deepseek"]
            )
        )

    # 篩選出成功初始化的評審客戶端
    active_reviewers = [r for r in reviewers if r.initialized_successfully]
    logging.info(
        f"Initialized reviewers (active for evaluation): {[r.model_name for r in active_reviewers]}"
    )
    # 記錄未成功初始化的評審客戶端
    inactive_reviewers = [
        r.model_name for r in reviewers if not r.initialized_successfully
    ]
    if inactive_reviewers:
        logging.info(
            f"Inactive reviewers (due to placeholder keys, etc.): {inactive_reviewers}"
        )

    # 儲存所有模型處理結果的列表
    all_results = []
    # 迭代處理設定檔中指定的每個 Ollama 模型
    for ollama_model_name in OLLAMA_MODELS_TO_COMPARE:
        logging.info(f"--- Processing Ollama model: {ollama_model_name} ---")
        # 準備用於報告的輸入文字片段
        input_snippet_for_report = (
            input_text[:200] + "..." if len(input_text) > 200 else input_text
        )
        # 初始化該模型的結果字典
        model_result = {
            "ollama_model": ollama_model_name,  # Ollama 模型名稱
            "task": args.task,  # 任務類型
            "input_text_snippet": input_snippet_for_report,  # 輸入文字片段
            "ollama_output": "<not_run>",  # Ollama 模型輸出，預設為未執行
            "reviews": [],  # 評審結果列表
        }
        try:
            # 使用 Ollama 客戶端產生輸出
            ollama_output = ollama_client.generate(
                ollama_model_name, input_text, args.task
            )
            model_result["ollama_output"] = ollama_output  # 更新模型輸出
            logging.info(f"Ollama model ({ollama_model_name}) mock output generated.")

            # 對於每個活躍的評審客戶端，進行評估
            for reviewer in active_reviewers:
                logging.info(f"Evaluating with mock reviewer {reviewer.model_name}...")
                try:
                    # 呼叫評審客戶端的 evaluate 方法
                    review_data = reviewer.evaluate(
                        input_text, ollama_output, args.task
                    )
                    # 將評審結果加入到模型結果中
                    model_result["reviews"].append(
                        {
                            "reviewer_model": reviewer.model_name,  # 評審模型名稱
                            "evaluation": review_data,  # 評估資料
                        }
                    )
                except Exception as e:
                    # 如果評審過程中發生錯誤，記錄錯誤訊息
                    logging.error(f"Mock reviewer {reviewer.model_name} error: {e}")
        except Exception as e:
            # 如果 Ollama 模型處理過程中發生錯誤，記錄錯誤訊息
            model_result["ollama_output"] = {"error": str(e)}  # 更新模型輸出為錯誤訊息
            logging.error(f"Mock Ollama model {ollama_model_name} error: {e}")
        # 將該模型的處理結果加入到總結果列表中
        all_results.append(model_result)

    logging.info("--- All models processed (mock) ---")
    # 嘗試產生並儲存報告
    try:
        generate_report(all_results, args.output_report)  # 呼叫報告產生函數
        logging.info(
            f"Comparison report (from mock data) saved to: {args.output_report}"
        )
    except Exception as e:
        # 如果產生報告失敗，記錄錯誤訊息並印出 JSON 格式的結果
        logging.error(f"Failed to generate report from mock data: {e}")
        print(json.dumps(all_results, indent=4, ensure_ascii=False))


# 如果此腳本是作為主程式執行
if __name__ == "__main__":
    main()  # 呼叫 main 函數
