from hallucination_engine import retrieve_and_rank

# Take user inputs
question = input("Enter question: ")
llm_answer = input("Paste LLM answer: ")

# Retrieve and rank evidence, get confidence
top_evidence, top_scores, confidence = retrieve_and_rank(question, llm_answer, top_k=20)

# Display top evidence
print("\nTop Evidence:")
for i, (text, score) in enumerate(zip(top_evidence, top_scores), start=1):
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