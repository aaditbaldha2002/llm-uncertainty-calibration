# hallucination_engine.py (batch-optimized)

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import re
import requests
import os
import json

# -----------------------------
# CONFIG: Hugging Face API
# -----------------------------
HF_MODEL = "meta-llama/Llama-3-13b-instruct"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# -----------------------------
# Load models & data
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("kb_index.faiss")
kb_df = pd.read_pickle("kb_texts.pkl")
texts = kb_df["text"].tolist()

# -----------------------------
# Utility functions
# -----------------------------
def extract_claims(answer):
    """Split an LLM answer into smaller factual claims"""
    claims = re.split(r"[.!?]", answer)
    claims = [c.strip() for c in claims if len(c.strip()) > 0]
    return claims

def retrieve_evidence(query, top_k=20):
    """Retrieve top-k relevant evidence from FAISS"""
    query_embedding = model.encode([query], convert_to_numpy=True)
    query_embedding /= np.linalg.norm(query_embedding, axis=1, keepdims=True)

    scores, indices = index.search(query_embedding, top_k)
    evidence_texts = [texts[i] for i in indices[0]]
    return evidence_texts

def compute_similarity(text, evidence_texts):
    """Compute similarity-based confidence score"""
    text_embedding = model.encode([text], convert_to_numpy=True)
    text_embedding /= np.linalg.norm(text_embedding, axis=1, keepdims=True)

    evidence_embeddings = model.encode(evidence_texts, convert_to_numpy=True)
    evidence_embeddings /= np.linalg.norm(evidence_embeddings, axis=1, keepdims=True)

    similarities = np.dot(evidence_embeddings, text_embedding.T).flatten()
    max_similarity = np.max(similarities)
    mean_similarity = np.mean(similarities)
    confidence = float(0.9 * max_similarity + 0.1 * mean_similarity)

    return confidence, similarities

# -----------------------------
# Hugging Face API call (batched)
# -----------------------------
def verify_claims_hf_batch(claims, evidence_texts, batch_size=5):
    """Verify multiple claims in a single API call"""
    # Chunk claims
    claim_batches = [claims[i:i+batch_size] for i in range(0, len(claims), batch_size)]
    all_results = []

    context = "\n".join(evidence_texts[:5])  # top-5 evidence for context

    for batch in claim_batches:
        # Build prompt with all claims in the batch
        claims_str = "\n".join([f"- {c}" for c in batch])
        prompt = (
            f"You are a fact-checking assistant. For each claim below, determine if it is supported by the evidence.\n\n"
            f"Claims:\n{claims_str}\n\n"
            f"Evidence:\n{context}\n\n"
            "Answer in JSON list format: [{'claim':'...', 'verdict':'true|false|unsupported','reasoning':'...'}, ...]"
        )
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 500}}

        try:
            response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            text = result[0]["generated_text"]

            try:
                # Extract JSON list
                batch_results = json.loads(re.search(r"\[.*\]", text, re.DOTALL).group())
            except Exception:
                # Fallback: mark all as unsupported if parsing fails
                batch_results = [{"claim": c, "verdict": "unsupported", "reasoning": text.strip()} for c in batch]

            all_results.extend(batch_results)

        except Exception as e:
            # On API failure, mark all claims in batch as unsupported
            all_results.extend([{"claim": c, "verdict": "unsupported", "reasoning": f"API call failed: {e}"} for c in batch])

    return all_results

# -----------------------------
# Main hallucination detection (batched)
# -----------------------------
def retrieve_and_verify_batch(question, llm_answer, top_k=20, batch_size=5):
    """Full pipeline: retrieve evidence, similarity scoring, and batch verification"""
    query = question + " " + llm_answer
    evidence_texts = retrieve_evidence(query, top_k)
    claims = extract_claims(llm_answer)

    claim_confidences = []
    for claim in claims:
        sim_conf, _ = compute_similarity(claim, evidence_texts)
        claim_confidences.append(sim_conf)

    # Hugging Face batch verification
    hf_verdicts = verify_claims_hf_batch(claims, evidence_texts, batch_size=batch_size)

    # Final confidence: strongest similarity claim
    final_confidence = float(max(claim_confidences))

    # Rank evidence by similarity to full answer
    _, similarities = compute_similarity(llm_answer, evidence_texts)
    sorted_indices = np.argsort(similarities)[::-1]
    top_evidence = [evidence_texts[i] for i in sorted_indices]
    top_scores = [similarities[i] for i in sorted_indices]

    return {
        "claims": claims,
        "similarity_confidences": claim_confidences,
        "hf_verdicts": hf_verdicts,
        "top_evidence": top_evidence,
        "top_scores": top_scores,
        "final_confidence": final_confidence,
    }