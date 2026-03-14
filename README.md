# LLM Hallucination Calibration System

This project allows users to **evaluate LLM-generated answers** for potential hallucinations. Users can enter a question and paste an LLM answer, and the system provides:

- A **hallucination confidence score** (0–1)  
- **Top evidence** supporting the answer  
- Factuality interpretation (`Likely factual`, `Partially supported`, `Potential hallucination`)

The system is implemented as a **Python backend** with a **Chrome Extension frontend**.

---

## 🔹 Features

- RAG-based evidence retrieval with FAISS
- Sentence embeddings using **`all-MiniLM-L6-v2`**
- Cosine similarity-based hallucination scoring
- Chrome Extension interface for seamless user interaction

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

### 4. Prepare the knowledge base
- Ensure you have generated `kb_index.faiss` and `kb_texts.pkl` files
- These are required for evidence retrieval

### 5. Run the python backend
```bash
python test_engine.py
```
- This launches a console interface for testing
- Enter a question and paste an LLM answer to see confidence scores and top evidence

## Load the Chrome Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable Developer Mode (top right)
3. Click Load unpacked
4. Select the folder chrome_extension in the project repository.
5. Pin the extension for easy access

Now you can click the extesion icon, input a question and LLM answer and see confidence scores + top evidence in real-time

## Project Structure
llm-hallucination-calibration/
├─ hallucination_engine.py   # Core scoring & retrieval logic
├─ test_engine.py           # Console testing interface
├─ kb_index.faiss           # FAISS index of knowledge base
├─ kb_texts.pkl             # Pickled KB texts
├─ chrome_extension/        # Chrome Extension frontend
│   ├─ manifest.json
│   ├─ popup.html
│   └─ popup.js
├─ datasets/                # Original datasets (TruthfulQA, HotpotQA, SQuAD, etc.)
└─ README.md
