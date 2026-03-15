from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hallucination_engine import retrieve_and_rank

app = FastAPI()

# CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QARequest(BaseModel):
    question: str
    answer: str

@app.post("/evaluate")
def evaluate(req: QARequest):
    # Run hallucination engine
    claims, claim_scores, top_evidence, top_scores, final_confidence = retrieve_and_rank(
        req.question, req.answer
    )

    # Convert numpy types to native Python types for JSON
    claim_scores = [float(s) for s in claim_scores]
    top_scores = [float(s) for s in top_scores]
    final_confidence = float(final_confidence)

    return {
        "confidence": final_confidence,
        "claims": claims,
        "claim_scores": claim_scores,
        "evidence": top_evidence[:3],
        "evidence_scores": top_scores[:3]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)