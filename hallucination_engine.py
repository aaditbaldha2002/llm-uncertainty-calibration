from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import re

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("kb_index.faiss")

# Load KB texts
kb_df = pd.read_pickle("kb_texts.pkl")
texts = kb_df["text"].tolist()


def extract_claims(answer):
    """
    Split an LLM answer into smaller factual claims
    """
    claims = re.split(r"[.!?]", answer)
    claims = [c.strip() for c in claims if len(c.strip()) > 0]
    return claims


def retrieve_evidence(query, top_k=20):

    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding /= np.linalg.norm(query_embedding, axis=1, keepdims=True)

    scores, indices = index.search(query_embedding, top_k)
    evidence_texts = [texts[i] for i in indices[0]]

    return evidence_texts


def compute_similarity(text, evidence_texts):

    text_embedding = model.encode([text], convert_to_numpy=True)
    text_embedding /= np.linalg.norm(text_embedding, axis=1, keepdims=True)

    evidence_embeddings = model.encode(evidence_texts, convert_to_numpy=True)
    evidence_embeddings /= np.linalg.norm(evidence_embeddings, axis=1, keepdims=True)

    similarities = np.dot(evidence_embeddings, text_embedding.T).flatten()

    max_similarity = np.max(similarities)
    mean_similarity = np.mean(similarities)

    confidence = float(0.7 * max_similarity + 0.3 * mean_similarity)

    return confidence, similarities


def retrieve_and_rank(question, llm_answer, top_k=20):

    # Improved retrieval query
    query = question + " " + llm_answer

    evidence_texts = retrieve_evidence(query, top_k)

    # Extract claims
    claims = extract_claims(llm_answer)

    claim_scores = []

    for claim in claims:
        score, similarities = compute_similarity(claim, evidence_texts)
        claim_scores.append(score)

    # Final answer confidence (weakest claim determines reliability)
    final_confidence = float(min(claim_scores))

    # Rank evidence based on full answer similarity
    _, similarities = compute_similarity(llm_answer, evidence_texts)

    sorted_indices = np.argsort(similarities)[::-1]

    top_evidence = [evidence_texts[i] for i in sorted_indices]
    top_scores = [similarities[i] for i in sorted_indices]

    return claims, claim_scores, top_evidence, top_scores, final_confidence