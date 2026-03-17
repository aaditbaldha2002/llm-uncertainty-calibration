# LLM Hallucination Calibration System

A Chrome Extension + Python backend that evaluates LLM-generated answers for potential hallucinations, returning a confidence score, supporting evidence, and a factuality verdict.

---

## 🌐 Demo & Write-up

| | |
|---|---|
| 📝 LinkedIn post + demo | [View on LinkedIn](https://www.linkedin.com/posts/aaditharshalbaldha_machinelearning-nlp-llm-activity-7439475072890736640-80XL?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEYe8K4BbgTA5u7uZr3n2SBttJuthnkgSXg) |
| 💻 Source code | [github.com/aaditbaldha2002/llm-uncertainty-calibration](https://github.com/aaditbaldha2002/llm-uncertainty-calibration) |

---

## 🔹 Features

- Hallucination confidence score (0–1)
- Top evidence passages supporting or contradicting the answer
- Factuality verdict: `Likely factual` · `Partially supported` · `Potential hallucination`
- RAG-based retrieval with FAISS + `all-MiniLM-L6-v2` sentence embeddings
- Two-stage verification: cosine similarity scoring + Llama 3 claim verification
- Chrome Extension UI for seamless browser-based interaction

---

## ⚙️ How It Works

**Stage 1 — Semantic Similarity**
Each claim in the LLM answer is sentence-split, encoded into vectors via `all-MiniLM-L6-v2`, and compared against a FAISS-indexed knowledge base using cosine similarity. This produces a per-claim confidence score.

**Stage 2 — LLM Verification**
Top retrieved evidence passages are passed alongside the claims to Llama 3 via the HuggingFace Inference API. The model returns a structured verdict (`true`, `false`, or `unsupported`) with reasoning. Both stages combine into a final weighted confidence score.

### Examples

```
Q: What is the capital of France?
A: Paris is the capital of France.
→ Confidence: ~0.85 | Verdict: Likely Factual ✅

Q: What is photosynthesis?
A: Photosynthesis is a financial process where banks convert currency
   reserves into liquid assets using quantum algorithms developed by MIT in 2003.
→ Confidence: ~0.21 | Verdict: Potential Hallucination 🚨
```

---

## 📦 Prerequisites

- Python 3.9+
- [Anaconda](https://www.anaconda.com/products/distribution) (recommended)
- Google Chrome
- HuggingFace API token

---

## ⚡ Setup

### 1. Clone the repository
```bash
git clone https://github.com/aaditbaldha2002/llm-uncertainty-calibration.git
cd llm-uncertainty-calibration
```

### 2. Create and activate the Conda environment
```bash
conda env create -f environment.yml
conda activate llm-hallucination-calibration
```

Or install dependencies directly:
```bash
pip install -r requirements.txt
```

### 3. Set your HuggingFace API token
```bash
export HF_API_TOKEN=your_token_here
```

### 4. Prepare the knowledge base

Place your knowledge base CSV at `data/knowledge_base.csv` with a single `text` column — one passage per row:

```
text
"The Eiffel Tower is located in Paris, France."
"Water boils at 100 degrees Celsius at sea level."
```

Three datasets are included in `datasets/` — use one to get started:
```bash
cp datasets/truthfulqa_processed.csv data/knowledge_base.csv
```

| Dataset | Description |
|---|---|
| `truthfulqa_processed.csv` | Factual Q&A pairs for hallucination benchmarking |
| `hotpotqa_processed.csv` | Multi-hop reasoning passages |
| `squad_processed.csv` | Reading comprehension passages |

### 5. Build the FAISS index
```bash
python build_kb.py
```

This encodes all passages and saves two files to `vector_db/`:

| File | Description |
|---|---|
| `kb_index.faiss` | FAISS index for nearest-neighbour retrieval |
| `kb_texts.pkl` | DataFrame mapping index positions to original text |

> ⚠️ Both files are required for the API server to start. Re-run `build_kb.py` any time you update `knowledge_base.csv`.

### 6. Run the backend
```bash
python api_server.py
```

API available at `http://127.0.0.1:8000`. To test without the extension:
```bash
python test_engine.py
```

### 7. Load the Chrome Extension

1. Go to `chrome://extensions/`
2. Enable **Developer Mode** (top-right toggle)
3. Click **Load unpacked** → select the `chrome_extension/` folder
4. Pin the extension for easy access

Enter a question and an LLM-generated answer in the popup to see the confidence score, verdict, and top supporting evidence.

---

## 📁 Project Structure

```
llm-hallucination-calibration/
├── hallucination_engine.py   # Core scoring & retrieval logic
├── api_server.py             # FastAPI backend
├── build_kb.py               # FAISS index builder
├── test_engine.py            # Console testing interface
├── data/
│   └── knowledge_base.csv    # Input data (user-provided)
├── vector_db/
│   ├── kb_index.faiss        # Generated FAISS index (gitignored)
│   └── kb_texts.pkl          # Generated KB texts (gitignored)
├── chrome_extension/
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
├── datasets/                 # Source datasets
├── environment.yml
├── requirements.txt
└── README.md
```

---

## ⚠️ Known Limitations

This is a research prototype. These constraints matter for interpreting results correctly.

**Semantic similarity ≠ factual accuracy**
`all-MiniLM-L6-v2` measures how semantically *related* two passages are — not whether a claim is *correct*. A plausible but wrong answer on the right topic (e.g. "The telephone was invented by Thomas Edison") can score similarly to the correct one because the surrounding vocabulary is too similar for the embedder to distinguish.

**Static knowledge base**
Claims are only verified against the pre-built FAISS index. Facts outside TruthfulQA / HotpotQA / SQuAD will return low confidence regardless of whether they're true.

**Sentence-based claim splitting**
Complex multi-clause sentences may not split cleanly into individually verifiable claims, which can affect per-claim scoring accuracy.

---

## 🔭 Future Work

- **NLI-based verification** — Replace cosine similarity with DeBERTa fine-tuned on MNLI, trained specifically on contradiction detection
- **Web Search RAG Agent** — When hallucination is flagged, trigger a live Tavily web search to retrieve cited corrections — turning the system from a passive detector into an active fact-correction tool
- **Cloud deployment** — Deploy backend to AWS Lambda or GCP Cloud Run to remove the local setup requirement
- **Broader benchmarking** — Evaluate against FEVER and HaluEval datasets for more rigorous, held-out performance measurement

---

## 🧪 Evaluation

Formal benchmarking requires a held-out dataset separate from the knowledge base. Testing against the same datasets used to build the KB (TruthfulQA, HotpotQA, SQuAD) would inflate results due to data overlap.

Manual testing shows the system reliably distinguishes:
- **Off-topic fabrications** → consistently low scores (< 0.4)
- **Direct factual matches** → consistently high scores (> 0.85)

The system struggles with **plausible but incorrect answers on the correct topic** — a known limitation of embedding-based approaches. Rigorous held-out evaluation against FEVER or HaluEval is planned as future work.
