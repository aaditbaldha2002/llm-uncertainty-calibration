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

    # Encode answer
    answer_embedding = model.encode([llm_answer], convert_to_numpy=True)
    answer_embedding = answer_embedding / np.linalg.norm(answer_embedding, axis=1, keepdims=True)

    # Encode all evidence at once
    evidence_embeddings = model.encode(evidence_texts, convert_to_numpy=True)
    evidence_embeddings = evidence_embeddings / np.linalg.norm(evidence_embeddings, axis=1, keepdims=True)

    # Compute cosine similarities (vectorized)
    similarities = np.dot(evidence_embeddings, answer_embedding.T).flatten()

    # Improved scoring logic
    max_similarity = np.max(similarities)
    mean_similarity = np.mean(similarities)

    confidence = float(0.7 * max_similarity + 0.3 * mean_similarity)

    return confidence, similarities