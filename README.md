# LLM Hallucination Calibration System

This project allows users to **evaluate LLM-generated answers** for potential hallucinations. Users can enter a question and paste an LLM answer, and the system provides:

- A **hallucination confidence score** (0–1)
- **Top evidence** supporting the answer
- Factuality interpretation (`Likely factual`, `Partially supported`, `Potential hallucination`)

The system is implemented as a **Python backend** with a **Chrome Extension frontend**.

---

## 🔹 Features

- RAG-based evidence retrieval with FAISS
- Sentence embeddings using `all-MiniLM-L6-v2`
- Two-stage verification: cosine similarity scoring + LLM-based claim verification
- Chrome Extension interface for seamless browser-based interaction

---

## 📦 Prerequisites

- Python 3.9+
- [Anaconda](https://www.anaconda.com/products/distribution) (recommended)
- Google Chrome

---

## ⚡ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/llm-hallucination-calibration.git
cd llm-hallucination-calibration
```

### 2. Create and activate the Conda environment
```bash
conda env create -f environment.yml
conda activate llm-hallucination-calibration
```

### 3. Install Python dependencies (if not using environment.yml)
```bash
pip install -r requirements.txt
```

### 4. Build the knowledge base

Before running the backend, you need to generate the FAISS index and knowledge base files from your dataset.

**Prepare your data**

Place your knowledge base CSV at `data/knowledge_base.csv`. The file must contain a `text` column with one passage or fact per row.

Supported datasets (included in `datasets/`):
- **TruthfulQA** — factual Q&A pairs for hallucination benchmarking
- **HotpotQA** — multi-hop reasoning passages
- **SQuAD** — reading comprehension passages

To use one of the included datasets:
```bash
cp datasets/truthfulqa_processed.csv data/knowledge_base.csv
```

Expected CSV format:
```
text
"The Eiffel Tower is located in Paris, France."
"Water boils at 100 degrees Celsius at sea level."
```

**Run the index builder**
```bash
python build_kb.py
```

This script will:
- Load all passages from `data/knowledge_base.csv`
- Generate sentence embeddings using `all-MiniLM-L6-v2`
- Normalize embeddings for cosine similarity via inner product
- Build and save a FAISS `IndexFlatIP` index

Output files saved to `vector_db/`:

| File | Description |
|---|---|
| `kb_index.faiss` | FAISS index for fast nearest-neighbor retrieval |
| `kb_texts.pkl` | Pickled DataFrame mapping index positions to original text |

After running you should see:
```
Batches: 100%|████████████| 120/120 [00:14<00:00]
FAISS index created with 3847 entries.
```

> ⚠️ These files are required for the API server to start. If they are missing, the server will throw a `RuntimeError` on startup.

### 5. Run the backend
```bash
python api_server.py
```

The API will be available at `http://127.0.0.1:8000`. To test via console instead:
```bash
python test_engine.py
```

### 6. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (top right toggle)
3. Click **Load unpacked**
4. Select the `chrome_extension/` folder from the repository
5. Pin the extension for easy access

Click the extension icon, enter a question and an LLM-generated answer, and see confidence scores and top supporting evidence in real time.

---

## 📁 Project Structure
```
llm-hallucination-calibration/
├── hallucination_engine.py   # Core scoring & retrieval logic
├── api_server.py             # FastAPI backend
├── build_kb.py               # FAISS index builder
├── test_engine.py            # Console testing interface
├── data/
│   └── knowledge_base.csv    # Input data for index (user-provided)
├── vector_db/
│   ├── kb_index.faiss        # Generated FAISS index (gitignored)
│   └── kb_texts.pkl          # Generated KB texts (gitignored)
├── chrome_extension/
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── datasets/                 # Source datasets (TruthfulQA, HotpotQA, SQuAD)
├── environment.yml
├── requirements.txt
└── README.md
```

---

## 📝 Notes

- Larger knowledge bases may take several minutes to encode on CPU
- Re-run `build_kb.py` any time you update `knowledge_base.csv` — the index does not auto-update
- `vector_db/` is gitignored by default — each collaborator should generate their own index locally
- Set your HuggingFace API token as an environment variable before running: `export HF_API_TOKEN=your_token_here`

## 🔭 Limitations & Future Work

- Cosine similarity captures semantic relatedness but not
  factual contradiction — NLI-based verification would improve
  precision on subtle hallucinations
- Current KB is static — a production system would need
  real-time retrieval from live knowledge sources
- **Web Search RAG Agent (planned):** When hallucination is 
  detected (confidence score below threshold), automatically 
  trigger a web search agent to retrieve live, cited sources 
  that either correct or confirm the claim — turning the system 
  from a passive detector into an active fact-correction tool
- Chrome Extension currently requires a local backend — 
  cloud deployment via AWS Lambda would enable public access
  without local setup
- Evaluation currently limited to TruthfulQA — broader 
  benchmarking across FEVER and HaluEval datasets planned
```

**Why this specific improvement is smart to mention:**

It shows you're thinking about the full user experience loop, not just the ML pipeline. The natural question after "this answer is hallucinated" is always "well what IS the correct answer?" — and you've already identified that gap and have a concrete architectural solution for it.

**If you ever actually implement it**, the technical approach would be:
```
Low confidence score detected
→ Extract the specific flagged claim
→ Pass claim to a search agent (SerpAPI / Tavily / DuckDuckGo API)
→ Retrieve top 3 web results
→ Run those results through your existing FAISS + similarity pipeline
→ Return corrected answer with cited sources back to Chrome Extension