# reporter.py
# 此檔案包含用於產生模型比較報告的函數。

import logging # 用於記錄程式運行訊息

# 設定日誌記錄的基本配置
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_report(all_results, output_filepath: str):
    """
    根據所有模型的處理結果產生 Markdown 格式的比較報告。

    Args:
        all_results (list): 一個包含每個模型處理結果的字典列表。
                            每個字典應包含 'ollama_model', 'task', 'input_text_snippet',
                            'ollama_output', 和 'reviews' 等鍵。
        output_filepath (str): 要儲存 Markdown 報告的檔案路徑。
    """
    # report_lines: 用於儲存報告的每一行內容的列表
    report_lines = []
    report_lines.append("# LLM 模型比較報告") # 報告主標題
    report_lines.append("") # 空行

    # 檢查是否有結果可報告
    if not all_results:
        report_lines.append("沒有可報告的結果。") # 如果沒有結果，則加入此訊息
        # 將空報告寫入檔案
        with open(output_filepath, "w", encoding="utf-8") as f_err:
            for line_err in report_lines:
                f_err.write(line_err + "\n")
        logging.info(f"已產生空報告到: {output_filepath}") # 記錄已產生空報告
        return # 結束函數

    # 取得第一個結果，用於提取任務類型和輸入片段等共享資訊
    first_result = all_results[0]
    # task_type: 從第一個結果中獲取任務類型，若無則設為 "未知任務"
    task_type = first_result.get("task", "未知任務")
    # task_display_name: 用於報告中顯示的任務名稱，預設為 task_type
    task_display_name = task_type
    try:
        # 嘗試從 config 模組導入 SUPPORTED_TASKS 以獲取更友好的任務顯示名稱
        from config import SUPPORTED_TASKS
        task_display_name = SUPPORTED_TASKS.get(task_type, task_type)
    except ImportError:
        # 如果導入失敗，記錄警告
        logging.warning("reporter.py: Could not import SUPPORTED_TASKS from config.")

    report_lines.append(f"## 任務: {task_display_name}") # 加入任務標題
    # input_snippet: 從第一個結果中獲取輸入文字片段，若無則設為 "N/A"
    input_snippet = first_result.get("input_text_snippet", "N/A")
    report_lines.append(
        f"### 輸入文本 (片段):\n> {input_snippet.replace('\n', '\n> ')}" # 加入輸入文字片段，並處理換行
    )
    report_lines.append("") # 空行

    # 迭代處理每個模型的結果
    for result in all_results:
        # ollama_model: 獲取當前處理的 Ollama 模型名稱
        ollama_model = result.get("ollama_model", "N/A")
        report_lines.append(f"--- --- ---\n### Ollama 模型: {ollama_model}\n") # 加入 Ollama 模型的分隔線和標題

        # 處理 Ollama 模型的輸出
        ollama_output = result.get("ollama_output") # 獲取 Ollama 模型的輸出
        report_lines.append("**Ollama 模型輸出:**") # 加入輸出標題
        if isinstance(ollama_output, dict) and "error" in ollama_output:
            # 如果輸出是字典且包含 'error' 鍵，表示發生錯誤
            report_lines.append(f"> _錯誤: {ollama_output['error']}_ ")
        elif ollama_output:
            # 如果有輸出內容，則加入報告，並處理換行
            report_lines.append(f"> {str(ollama_output).replace('\n', '\n> ')}")
        else:
            # 如果沒有輸出或輸出為空
            report_lines.append("> _無輸出或輸出為空。_")
        report_lines.append("") # 空行

        # 處理評審結果
        reviews = result.get("reviews", []) # 獲取評審結果列表
        if reviews:
            report_lines.append("**評審結果:**") # 加入評審結果標題
        else:
            # 如果沒有評審結果
            report_lines.append("- _此 Ollama 模型沒有來自活躍評審員的評審結果。_")

        # 迭代處理每個評審
        for review in reviews:
            # reviewer_model: 獲取評審模型的名稱
            reviewer_model = review.get("reviewer_model", "N/A")
            # evaluation: 獲取評估資料
            evaluation = review.get("evaluation", {})
            report_lines.append(f"- **評審模型: {reviewer_model}**") # 加入評審模型名稱

            if isinstance(evaluation, dict) and "error" in evaluation:
                # 如果評估資料是字典且包含 'error' 鍵，表示評審時發生錯誤
                report_lines.append(f"  - _錯誤: {evaluation['error']}_ ")
            elif isinstance(evaluation, dict):
                # score_keys: 根據任務類型決定要顯示的評分項目
                score_keys = (
                    [
                        "accuracy_score", # 準確度評分
                        "fluency_score", # 流暢度評分
                        "traditional_chinese_usage_score", # 繁體中文用字評分
                    ]
                    if task_type == "translate" # 如果是翻譯任務
                    else [
                        "relevance_score", # 相關性評分
                        "completeness_score", # 完整性評分
                        "conciseness_score", # 簡潔性評分
                        "language_expression_score", # 語言表達評分
                    ]
                )
                # 加入總體評分
                report_lines.append(
                    f"  - 總體評分: {evaluation.get('overall_score', 'N/A')}"
                )
                # 迭代加入各項子評分
                for key in score_keys:
                    report_lines.append(
                        f"    - {key.replace('_score', '').replace('_', ' ').capitalize()}: {evaluation.get(key, 'N/A')}"
                    )
                # 加入評論文字
                report_lines.append(f"  - 評論: {evaluation.get('comment', '無評論')}")
            else:
                # 如果評估格式無法解析
                report_lines.append(
                    f"  - _無法解析的評估格式: {str(evaluation)[:100]}..._"
                )
            report_lines.append("") # 每個評審後加空行
        report_lines.append("") # 每個 Ollama 模型結果後加空行

    # 嘗試將報告內容寫入指定的輸出檔案
    try:
        with open(output_filepath, "w", encoding="utf-8") as f_main_report:
            for line_main_report in report_lines:
                f_main_report.write(line_main_report + "\n")
        logging.info(f"報告已儲存到: {output_filepath}") # 記錄報告儲存成功
    except Exception as e:
        # 如果儲存報告時發生錯誤，記錄錯誤並重新引發例外
        logging.error(f"儲存報告到 {output_filepath} 時發生錯誤: {e}")
        raise
