# reporter.py
import json
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_report(all_results, output_filepath: str):
    report_lines = []


    report_lines.append("# LLM 模型比較報告")
    report_lines.append("")


    if not all_results:
        report_lines.append("沒有可報告的結果。")
        with open(output_filepath, 'w', encoding='utf-8') as f_err:
            for line_err in report_lines:
                f_err.write(line_err + '\n')
        logging.info(f"已產生空報告到: {output_filepath}")
        return


    first_result = all_results[0]
    task_type = first_result.get('task', '未知任務')
    task_display_name = task_type
    try:
        from config import SUPPORTED_TASKS
        task_display_name = SUPPORTED_TASKS.get(task_type, task_type)
    except ImportError:
        logging.warning('reporter.py: Could not import SUPPORTED_TASKS from config. Using raw task type name.')


    report_lines.append(f"## 任務: {task_display_name}")
    input_snippet = first_result.get('input_text_snippet', '無輸入文本片段提供')
    report_lines.append("### 輸入文本 (片段):")
    report_lines.append(f"> {input_snippet.replace('\n', '\n> ')}")
    report_lines.append("")


    for result in all_results:
        ollama_model = result.get('ollama_model', '未知 Ollama 模型')
        report_lines.append("--- --- ---")
        report_lines.append(f"### Ollama 模型: {ollama_model}")
        report_lines.append("")


        ollama_output = result.get('ollama_output')
        report_lines.append("**Ollama 模型輸出:**")
        if isinstance(ollama_output, dict) and 'error' in ollama_output:
            report_lines.append(f"> _錯誤: {ollama_output['error']}_ ")
        elif ollama_output:
            report_lines.append(f"> {str(ollama_output).replace('\n', '\n> ')}")
        else:
            report_lines.append("> _無輸出或輸出為空。_")
        report_lines.append("")


        reviews = result.get('reviews', [])
        if reviews:
            report_lines.append("**評審結果:**")
            for review in reviews:
                reviewer_model = review.get('reviewer_model', '未知評審模型')
                evaluation = review.get('evaluation', {})
                report_lines.append(f"- **評審模型: {reviewer_model}**")
                if isinstance(evaluation, dict) and 'error' in evaluation:
                    report_lines.append(f"  - _錯誤: {evaluation['error']}_ ")
                    if 'raw_response' in evaluation:
                        report_lines.append(f"    - _原始回應: {str(evaluation['raw_response'])[:200]}..._")
                elif isinstance(evaluation, dict):
                    score_keys = []
                    if task_type == 'translate':
                        score_keys = ['accuracy_score', 'fluency_score', 'traditional_chinese_usage_score']
                    elif task_type == 'summarize':
                        score_keys = ['relevance_score', 'completeness_score', 'conciseness_score', 'language_expression_score']

                    overall_score = evaluation.get('overall_score', 'N/A')
                    report_lines.append(f"  - 總體評分: {overall_score}")
                    for key in score_keys:
                        if key in evaluation:
                            display_key = key.replace('_score', '').replace('_', ' ').capitalize()
                            report_lines.append(f"    - {display_key}: {evaluation[key]}")
                    comment = evaluation.get('comment', '無評論')
                    report_lines.append(f"  - 評論: {comment}")
                else:
                    report_lines.append(f"  - _無法解析的評估格式: {str(evaluation)[:200]}..._")
                report_lines.append("")
        else:
            report_lines.append("- _此 Ollama 模型沒有評審結果。_")
        report_lines.append("")


    try:
        with open(output_filepath, 'w', encoding='utf-8') as f_main_report:
            for line_main_report in report_lines:
                f_main_report.write(line_main_report + '\n')
        logging.info(f"報告已儲存到: {output_filepath}")
    except Exception as e:
        logging.error(f"儲存報告到 {output_filepath} 時發生錯誤: {e}")
        raise


if __name__ == '__main__':
    print("Executing reporter.py self-test...")
    dummy_config_content = "SUPPORTED_TASKS = {'translate': 'Translate to Trad. Chinese', 'summarize': 'Summarize Text'}"
    if not os.path.exists('config.py'):
        try:
            with open('config.py', 'w', encoding='utf-8') as cf:
                cf.write(dummy_config_content + '\n')
            print('reporter.py __main__: Temporary config.py created for self-test.')
        except Exception as e_conf:
            print(f'reporter.py __main__: Error creating temp config.py: {e_conf}')


    sample_results_translate = [
        {
            'task': 'translate',
            'input_text_snippet': 'Hello world. This is a test.',
            'ollama_model': 'gemma:2b',
            'ollama_output': '你好世界。這是一個測試。',
            'reviews': [
                {
                    'reviewer_model': 'gpt-3.5-turbo',
                    'evaluation': {
                        'accuracy_score': 4, 'fluency_score': 5, 'traditional_chinese_usage_score': 4,
                        'overall_score': 4.3, 'comment': '翻譯良好，流暢自然。'
                    }
                }
            ]
        }
    ]
    sample_report_path_translate = 'test_translation_report.md'
    success_flag = True
    try:
        generate_report(sample_results_translate, sample_report_path_translate)
        print(f"Self-test: Translation task test report generated to: {sample_report_path_translate}")
        if os.path.exists(sample_report_path_translate):
            with open(sample_report_path_translate, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'LLM 模型比較報告' in content and 'gemma:2b' in content and '你好世界' in content:
                    print('Self-test: Translation report content初步驗證成功。')
                else:
                    print('Self-test: Translation report content初步驗證失敗。')
                    success_flag = False
        else:
            print(f'Self-test: Report file {sample_report_path_translate} was not created.')
            success_flag = False
    except Exception as e:
        print(f"Self-test: Error during generate_report for translation: {e}")
        success_flag = False


    if not success_flag:
        print("reporter.py self-test FAILED.")
        exit(1)
    else:
        print("reporter.py self-test PASSED.")
