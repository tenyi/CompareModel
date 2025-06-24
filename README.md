# LLM 模型能力比較工具

本專案旨在提供一個 Python 工具，用於比較本地端 Ollama LLM 模型在繁體中文處理方面的能力，特別是翻譯和歸納總結。比較結果將由指定的雲端大型語言模型進行評審，並以 Markdown 格式產生報告。

## 主要功能

- **模型比較**: 支援比較多個在本地 Ollama 上運行的模型 (例如 gemma, deepseek-coder, qwen)。
- **多任務評估**: 可針對「英翻中」和「內容總結」兩種任務進行評估。
- **雲端 LLM 評審**: 使用指定的雲端大型語言模型 (例如 GPT 系列, Gemini 系列, DeepSeek 系列) 作為評審員，對 Ollama 模型的輸出進行結構化評分。
- **Markdown 報告**: 自動產生詳細的 Markdown 格式比較報告。

## 安裝需求

### 1. Python

- 本工具需要 Python 3.8 或更高版本。

### 2. Ollama

- 您需要在您的系統上安裝並運行 [Ollama](https://ollama.com/)。
- 請確保已透過 Ollama 下載您想要比較的模型。例如:

  ```bash
  ollama pull gemma:2b
  ollama pull qwen:4b # 根據您的需求調整模型名稱和版本
  ```

### 3. Python 套件

您可以使用 `pip` 或 `uv` 來安裝必要的 Python 套件。

**使用 `pip`:**

  ```bash
  pip install ollama openai google-generativeai requests
  ```

**使用 `uv` (一個快速的 Python 套件安裝器):**

  ```bash
  # 首先，如果您還沒有安裝 uv，請依照其官方指南安裝 (https://github.com/astral-sh/uv)
  uv pip install ollama openai google-generativeai requests
  ```

## 設定

在執行程式之前，您需要設定 `config.py` 檔案:

1. **複製範例設定 (如果提供)**: 如果專案中有 `config.py.example`，請複製一份並命名為 `config.py`。否則，請直接建立 `config.py`。
2. **編輯 `config.py`**:
    - `OLLAMA_API_BASE_URL`: 本地 Ollama 服務的 API 端點。預設為 `"http://localhost:11434"`，通常不需要修改。
    - `OLLAMA_MODELS_TO_COMPARE`: 一個 Python 列表，包含您想要比較的 Ollama 模型名稱 (包含標籤)。例如: `["gemma:2b", "qwen:4b"]`。請確保這些模型已經在您的 Ollama 中下載。
    - `OPENAI_API_KEY`: 您的 OpenAI API 金鑰。如果您不使用 OpenAI 模型進行評審，可以保留預留位置 `"YOUR_OPENAI_API_KEY"`。
    - `GOOGLE_API_KEY`: 您的 Google AI (Gemini) API 金鑰。如果您不使用 Gemini 模型進行評審，可以保留預留位置 `"YOUR_GOOGLE_API_KEY"`。
    - `DEEPSEEK_API_KEY`: 您的 DeepSeek API 金鑰 (如果 DeepSeek 提供 API 且您希望使用其作為評審模型)。目前 DeepSeek 評審用戶端主要作為模擬/佔位符。如果沒有金鑰或不使用，可保留預留位置 `"YOUR_DEEPSEEK_API_KEY"`。
    - `REVIEWER_MODELS`: 一個字典，定義了用於評審的雲端模型。預設包含 `gpt`、`gemini` 和 `deepseek` 的建議模型。您可以根據您的 API 存取權限調整模型名稱。
    - `SUPPORTED_TASKS`: 定義支援的任務類型及其描述，通常不需要修改。

**重要**: `config.py` 檔案包含敏感的 API 金鑰。此檔案已被預設加入 `.gitignore` 中，以避免意外將金鑰上傳到版本控制系統。請勿從 `.gitignore` 中移除 `config.py` 條目，除非您清楚相關風險。

## 使用方式

透過命令列執行 `main.py` 腳本:

```bash
python main.py --input_file <輸入檔案路徑> --task <任務類型> [--output_report <報告輸出路徑>]
```

**參數說明:**

- `--input_file`: (必須) 包含輸入文本的檔案路徑。
  - 對於「翻譯」任務，此檔案應包含您希望翻譯的英文句子或段落。
  - 對於「總結」任務，此檔案應包含您希望總結的文章內容。
- `--task`: (必須) 要執行的任務類型。目前支援:
  - `translate`: 進行英翻中（繁體）。
  - `summarize`: 進行內容總結（繁體中文輸出）。
- `--output_report`: (可選) 指定 Markdown 報告輸出的檔案路徑。預設為 `comparison_report.md`。

**範例指令:**

- **翻譯任務:**

  ```bash
  python main.py --input_file my_english_text.txt --task translate --output_report translation_results.md
  ```

- **總結任務:**

  ```bash
  python main.py --input_file my_article.txt --task summarize --output_report summary_results.md
  ```

程式執行完成後，會在指定的路徑產生 Markdown 格式的比較報告。

## 報告解讀

產生的 Markdown 報告將包含以下主要部分:

- **任務類型和輸入文本片段**: 清晰標示本次比較的任務及輸入內容摘要。
- **各 Ollama 模型表現**:
  - **模型名稱**: 標示正在比較的 Ollama 模型。
  - **Ollama 模型輸出**: 展示該模型針對輸入所產生的原始輸出。如果模型執行出錯，則會顯示錯誤訊息。
  - **評審結果**: 列出各個雲端評審模型對該 Ollama 模型輸出的評估。
    - **評審模型名稱**: 標示是哪個雲端模型進行的評審。
    - **各項評分**: 根據任務類型（翻譯或總結），展示不同維度的評分 (1-5 分，5 分最高)，例如準確性、流暢度、相關性等。
    - **總體評分**: 該評審模型給出的綜合分數。
    - **評論**: 評審模型提供的文字評語。
    - 如果評審過程中發生錯誤 (例如 API 金鑰無效)，也會在此處顯示錯誤訊息。

## 注意事項

- **Ollama 模型名稱**: `config.py` 中的 `OLLAMA_MODELS_TO_COMPARE` 列表需要填寫您在 Ollama 中實際下載並可用的模型名稱 (包含標籤，例如 `gemma:2b` 而非僅 `gemma`)。 `deepseek-r1` 這個模型名稱可能並非 Ollama Hub 上的官方名稱，您可能需要使用如 `deepseek-coder:6.7b` 或其他可用的 DeepSeek 系列模型。
- **DeepSeek 雲端評審**: DeepSeek 的公開雲端評審 API 及其 Python SDK 的情況可能不如 OpenAI 或 Gemini 明確。目前的 `DeepSeekReviewerClient` 主要作為一個模擬/佔位符，即使提供了 API 金鑰，它也可能只返回模擬的評審結果。
- **API 金鑰與費用**: 請注意，使用雲端 LLM (OpenAI, Gemini) 進行評審可能會產生 API 費用。請確保您了解相關的計費方式。
- **環境相容性**: 在極少數特殊的腳本執行環境 (例如某些雲端 IDE 或受限的 shell 環境) 中，`config.py` 的動態載入可能偶爾會遇到非預期的問題。如果遇到 `ImportError: No module named 'config'` 且您已確認 `config.py` 存在，請檢查您的執行環境限制。

## 貢獻

歡迎各種形式的貢獻，包括功能建議、問題回報、程式碼修正等。請透過 GitHub Issues 或 Pull Requests 參與。

## 授權條款

本專案採用 MIT 授權條款。詳情請見 `LICENSE` 檔案 (如果專案中包含)。
