from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("kb_index.faiss")

# Load KB texts
kb_df = pd.read_pickle("kb_texts.pkl")
texts = kb_df["text"].tolist()


def retrieve_evidence(query, top_k=20):
    
    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

    distances, indices = index.search(query_embedding, top_k)

    evidence = [texts[i] for i in indices[0]]

    return evidence, distances[0]


def hallucination_score(llm_answer, evidence_texts):

    answer_embedding = model.encode([llm_answer], convert_to_numpy=True)
    answer_embedding = answer_embedding / np.linalg.norm(answer_embedding, axis=1, keepdims=True)

    scores = []

    for text in evidence_texts:

        text_emb = model.encode([text], convert_to_numpy=True)
        text_emb = text_emb / np.linalg.norm(text_emb, axis=1, keepdims=True)

        similarity = np.dot(answer_embedding, text_emb.T)[0][0]
        scores.append(similarity)

    confidence = float(np.mean(scores))

    return confidence