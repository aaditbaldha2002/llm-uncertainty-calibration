# LLM Hallucination Calibration System

This project allows users to **evaluate LLM-generated answers** for potential hallucinations. Users can enter a question and paste an LLM answer, and the system provides:

- A **hallucination confidence score** (0–1)
- **Top evidence** supporting the answer
- Factuality interpretation (`Likely factual`, `Partially supported`, `Potential hallucination`)

The system is implemented as a **Python backend** with a **Chrome Extension frontend**.

---
🌐 Demo & Write-up
📝 LinkedIn Post with Demo → https://www.linkedin.com/posts/aaditharshalbaldha_machinelearning-nlp-llm-activity-7439475072890736640-80XL?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEYe8K4BbgTA5u7uZr3n2SBttJuthnkgSXg

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

## ⚙️ How It Works

The system uses a **two-stage pipeline** to evaluate LLM-generated answers for potential hallucinations:

**Stage 1 — Semantic Similarity Scoring**
Each claim in the LLM answer is split into individual sentences and encoded into vector embeddings using `all-MiniLM-L6-v2`. These embeddings are compared against the FAISS-indexed knowledge base using cosine similarity, producing a per-claim confidence score.

**Stage 2 — LLM-Based Claim Verification**
The top retrieved evidence passages are passed alongside the claims to a Llama 3 model via the HuggingFace Inference API. The model returns a structured verdict (`true`, `false`, or `unsupported`) with reasoning for each claim. Both stages are combined into a final weighted confidence score.

---

## ✅ What It Detects Well

The system is most reliable at flagging two specific failure modes:

- **Off-topic fabrications** — answers that use correct-sounding language but reference concepts, events, or entities completely unrelated to the question (e.g. describing photosynthesis as a financial process)
- **Direct factual mismatches** — answers where key facts directly contradict well-represented passages in the knowledge base

**Example — high confidence (factual answer):**
```
Q: What is the capital of France?
A: Paris is the capital of France.
→ Confidence: ~0.85 | Verdict: Likely Factual ✅
```

**Example — low confidence (off-topic fabrication):**
```
Q: What is photosynthesis?
A: Photosynthesis is a financial process where banks convert 
   currency reserves into liquid assets using quantum algorithms 
   developed by MIT in 2003.
→ Confidence: ~0.21 | Verdict: Potential Hallucination 🚨
```

---

## ⚠️ Known Limitations

This system is a research prototype. Understanding its constraints is important for correct interpretation of results.

**Semantic similarity ≠ factual accuracy**
The embedding model (`all-MiniLM-L6-v2`) measures how semantically related two passages are — not whether a claim is factually correct. A plausible but wrong answer about the correct topic (e.g. "The telephone was invented by Thomas Edison") may score similarly to the correct answer because the surrounding vocabulary and topic are the same. The model has no understanding of factual truth.

**Static knowledge base**
The system can only verify claims against its pre-built FAISS index. Facts outside the indexed datasets (TruthfulQA, HotpotQA, SQuAD) will return low confidence regardless of accuracy.

**Claim splitting is sentence-based**
Complex multi-clause sentences may not split cleanly into individual verifiable claims, which can affect per-claim scoring accuracy.

---

## 🔭 Future Work

- **NLI-based verification** — Replace or augment cosine similarity with a Natural Language Inference model (e.g. DeBERTa fine-tuned on MNLI) trained specifically on contradiction detection, improving precision on plausible but factually incorrect claims
- **Web Search RAG Agent** — When hallucination is detected (confidence below threshold), automatically trigger a web search agent (e.g. Tavily API) to retrieve live cited sources that correct the flagged claim — turning the system from a passive detector into an active fact-correction tool
- **Cloud deployment** — Deploy backend to AWS Lambda or GCP Cloud Run to remove the local setup requirement and enable public access via the Chrome Extension
- **Broader benchmarking** — Evaluate against FEVER and HaluEval datasets in addition to TruthfulQA to measure performance across diverse hallucination types

## 🧪 Evaluation

Formal benchmarking requires a held-out evaluation set separate from 
the system's knowledge base. Since the current KB is built from 
TruthfulQA, HotpotQA, and SQuAD, quantitative evaluation against 
these same datasets would produce artificially inflated results due 
to data overlap.

Manual testing shows the system reliably distinguishes between:
- **Off-topic fabrications** — answers using unrelated concepts 
  score consistently low (< 0.4)
- **Direct factual matches** — answers closely matching KB content 
  score consistently high (> 0.85)

The system struggles with **plausible but incorrect answers** on the 
correct topic — a known limitation of embedding-based similarity 
approaches documented in the Limitations section.

Rigorous evaluation against a fully held-out dataset (FEVER or 
HaluEval) is planned as part of future work.