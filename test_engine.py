from hallucination_engine import retrieve_evidence, hallucination_score, get_top_evidence

# Take user inputs
question = input("Enter question: ")
llm_answer = input("Paste LLM answer: ")

# Retrieve evidence and raw similarity scores
evidence, _ = retrieve_evidence(question, top_k=20)

# Compute hallucination confidence and similarities
confidence, similarities = hallucination_score(llm_answer, evidence)

# Get top 3 supporting evidence
top_evidence = get_top_evidence(evidence, similarities, k=3)

# Display top evidence
print("\nTop Evidence:")
for i, (text, score) in enumerate(top_evidence, start=1):
    print(f"\nEvidence {i} (Score: {round(score, 3)}):")
    print(text[:400])  # Preview first 400 chars

# Display hallucination confidence
print("\nHallucination Confidence Score:", round(confidence, 4))

# Interpret results
if confidence > 0.75:
    print("✅ Answer likely factual")
elif confidence > 0.5:
    print("⚠️ Answer partially supported")
else:
    print("❌ Potential hallucination detected")