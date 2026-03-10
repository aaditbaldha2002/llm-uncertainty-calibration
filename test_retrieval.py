from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np

# Load FAISS index and texts
index = faiss.read_index("kb_index.faiss")
kb_df = pd.read_pickle("kb_texts.pkl")
texts = kb_df['text'].tolist()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_evidence(query, top_k=5):
    query_emb = model.encode([query], convert_to_numpy=True)
    query_emb = query_emb / np.linalg.norm(query_emb, axis=1, keepdims=True)
    distances, indices = index.search(query_emb, top_k)
    retrieved_texts = [texts[i] for i in indices[0]]
    return retrieved_texts, distances[0]

# Test example
question = "When did Beyoncé go solo?"
evidence_texts, sims = retrieve_evidence(question, top_k=5)
for i, text in enumerate(evidence_texts):
    print(f"\nEvidence {i+1} (score {sims[i]:.3f}):\n{text}")