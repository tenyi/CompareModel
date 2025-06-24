# reporter.py
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_report(all_results, output_filepath: str):
    report_lines = []
    report_lines.append("# LLM 模型比較報告")
    report_lines.append("")
    if not all_results:
        report_lines.append("沒有可報告的結果。")
        with open(output_filepath, "w", encoding="utf-8") as f_err:
            for line_err in report_lines:
                f_err.write(line_err + "\n")
        logging.info(f"已產生空報告到: {output_filepath}")
        return
    first_result = all_results[0]
    task_type = first_result.get("task", "未知任務")
    task_display_name = task_type
    try:
        from config import SUPPORTED_TASKS

        task_display_name = SUPPORTED_TASKS.get(task_type, task_type)
    except ImportError:
        logging.warning("reporter.py: Could not import SUPPORTED_TASKS from config.")
    report_lines.append(f"## 任務: {task_display_name}")
    input_snippet = first_result.get("input_text_snippet", "N/A")
    report_lines.append(
        f"### 輸入文本 (片段):\n> {input_snippet.replace('\n', '\n> ')}"
    )
    report_lines.append("")
    for result in all_results:
        ollama_model = result.get("ollama_model", "N/A")
        report_lines.append(f"--- --- ---\n### Ollama 模型: {ollama_model}\n")
        ollama_output = result.get("ollama_output")
        report_lines.append("**Ollama 模型輸出:**")
        if isinstance(ollama_output, dict) and "error" in ollama_output:
            report_lines.append(f"> _錯誤: {ollama_output['error']}_ ")
        elif ollama_output:
            report_lines.append(f"> {str(ollama_output).replace('\n', '\n> ')}")
        else:
            report_lines.append("> _無輸出或輸出為空。_")
        report_lines.append("")
        reviews = result.get("reviews", [])
        if reviews:
            report_lines.append("**評審結果:**")
        else:
            report_lines.append("- _此 Ollama 模型沒有來自活躍評審員的評審結果。_")
        for review in reviews:
            reviewer_model = review.get("reviewer_model", "N/A")
            evaluation = review.get("evaluation", {})
            report_lines.append(f"- **評審模型: {reviewer_model}**")
            if isinstance(evaluation, dict) and "error" in evaluation:
                report_lines.append(f"  - _錯誤: {evaluation['error']}_ ")
            elif isinstance(evaluation, dict):
                score_keys = (
                    [
                        "accuracy_score",
                        "fluency_score",
                        "traditional_chinese_usage_score",
                    ]
                    if task_type == "translate"
                    else [
                        "relevance_score",
                        "completeness_score",
                        "conciseness_score",
                        "language_expression_score",
                    ]
                )
                report_lines.append(
                    f"  - 總體評分: {evaluation.get('overall_score', 'N/A')}"
                )
                for key in score_keys:
                    report_lines.append(
                        f"    - {key.replace('_score', '').replace('_', ' ').capitalize()}: {evaluation.get(key, 'N/A')}"
                    )
                report_lines.append(f"  - 評論: {evaluation.get('comment', '無評論')}")
            else:
                report_lines.append(
                    f"  - _無法解析的評估格式: {str(evaluation)[:100]}..._"
                )
            report_lines.append("")
        report_lines.append("")
    try:
        with open(output_filepath, "w", encoding="utf-8") as f_main_report:
            for line_main_report in report_lines:
                f_main_report.write(line_main_report + "\n")
        logging.info(f"報告已儲存到: {output_filepath}")
    except Exception as e:
        logging.error(f"儲存報告到 {output_filepath} 時發生錯誤: {e}")
        raise
