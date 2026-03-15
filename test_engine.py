from hallucination_engine import retrieve_and_rank

# Take user inputs
question = input("Enter question: ")
llm_answer = input("Paste LLM answer: ")

claims, claim_scores, top_evidence, top_scores, confidence = retrieve_and_rank(
    question, llm_answer, top_k=20
)

# Display claims and their scores
print("\nDetected Claims:")
for i, (claim, score) in enumerate(zip(claims, claim_scores), start=1):
    print(f"\nClaim {i}: {claim}")
    print(f"Confidence: {round(score,4)}")

# Display top evidence
print("\nTop Evidence:")
for i, (text, score) in enumerate(zip(top_evidence, top_scores), start=1):
    print(f"\nEvidence {i} (Score: {round(score,3)}):")
    print(text[:400])

# Display hallucination confidence
print("\nFinal Hallucination Confidence Score:", round(confidence,4))

if confidence > 0.75:
    print("✅ Answer likely factual")
elif confidence > 0.5:
    print("⚠️ Answer partially supported")
else:
    print("❌ Potential hallucination detected")