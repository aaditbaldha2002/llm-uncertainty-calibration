# api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hallucination_engine import retrieve_and_verify_batch

app = FastAPI()

# CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class QARequest(BaseModel):
    question: str
    answer: str

# Endpoint to evaluate hallucinations
@app.post("/evaluate")
def evaluate(req: QARequest):
    # Run hallucination engine
    results = retrieve_and_verify_batch(req.question, req.answer)

    # Convert numpy types to native Python types for JSON serialization
    claim_scores = [float(s) for s in results["similarity_confidences"]]
    top_scores = [float(s) for s in results["top_scores"]]
    final_confidence = float(results["final_confidence"])

    return {
        "confidence": final_confidence,
        "claims": results["claims"],
        "claim_scores": claim_scores,
        "hf_verdicts": results["hf_verdicts"],  # Hugging Face LLM verdicts
        "top_evidence": results["top_evidence"][:3],  # top 3 evidence snippets
        "top_scores": top_scores[:3],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)