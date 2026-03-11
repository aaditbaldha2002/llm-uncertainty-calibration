from fastapi import FastAPI
from pydantic import BaseModel
from hallucination_engine import retrieve_evidence, hallucination_score

app = FastAPI()

class QARequest(BaseModel):
    question: str
    answer: str


@app.post("/evaluate")
def evaluate(req: QARequest):

    evidence, sims = retrieve_evidence(req.question)
    confidence = hallucination_score(req.answer, evidence)

    return {
        "confidence": confidence,
        "evidence": evidence[:3]
    }