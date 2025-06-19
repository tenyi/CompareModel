# LLM 模型能力比較工具

本專案旨在提供一個 Python 工具，用於比較本地端 Ollama LLM 模型在繁體中文處理方面的能力，特別是翻譯和歸納總結。

## 功能
- 支援比較多個 Ollama 上運行的模型 (例如 [gemma3](https://ollama.com/library/gemma3), [DeepSeek-R1](https://ollama.com/library/deepseek-r1), [qwen3](https://ollama.com/library/qwen3)， [Breeze2](https://ollama.com/willqiu/Llama-Breeze2-8B-Instruct))。
- 使用雲端大型語言模型 (GPT-4.1, Gemini-2.5-Flash, DeepSeek) 作為評審。
- 針對翻譯和歸納總結能力進行評估。
- 產生比較報告。

## 設定

1.  **安裝必要的 Python 函式庫:**
    ```bash
    pip install requests openai google-generativeai
    # 如果 Ollama 有 Python 函式庫，也請一併安裝
    # pip install ollama
    ```

2.  **設定 Ollama:**
    確保您的 Ollama 服務正在運行，並且已經下載了您想要比較的模型。
    ```bash
    ollama pull gemma:7b
    ollama pull deepseek-coder:6.7b # 根據您實際使用的模型調整
    ollama pull qwen:7b
    ```

3.  **設定 API 金鑰:**
    複製 `config.py.example` (如果提供) 或直接編輯 `config.py` 檔案，並填入您的 API 金鑰：
    - `OLLAMA_API_BASE_URL`: 本地 Ollama 服務的 URL (預設為 `http://localhost:11434`)。
    - `OLLAMA_MODELS_TO_COMPARE`: 您想要比較的 Ollama 模型列表，例如 `["gemma:7b", "deepseek-coder:6.7b", "qwen:7b"]`。請確保這些模型已經在您的 Ollama 中下載。
    - `OPENAI_API_KEY`: 您的 OpenAI API 金鑰。
    - `GOOGLE_API_KEY`: 您的 Google AI (Gemini) API 金鑰。
    - `DEEPSEEK_API_KEY`: 您的 DeepSeek API 金鑰 (如果 DeepSeek 提供 API 且您希望使用)。

    **重要:** `config.py` 包含敏感的 API 金鑰，預設已被加入 `.gitignore` 以避免意外上傳到版本控制系統。請勿移除 `.gitignore` 中的 `config.py` 條目，除非您確定要追蹤此檔案。

## 使用方式

```bash
python main.py --input_file <您的文本檔案路徑> --task <translate|summarize>
```
例如:
```bash
python main.py --input_file my_article.txt --task summarize
python main.py --input_file english_sentences.txt --task translate
```

程式將會輸出比較報告。

