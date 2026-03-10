from hallucination_engine import retrieve_evidence, hallucination_score

question = input("Enter question: ")
llm_answer = input("Paste LLM answer: ")

evidence, sims = retrieve_evidence(question)

confidence = hallucination_score(llm_answer, evidence)

print("\nTop Evidence:")
for i, text in enumerate(evidence):
    print(f"\nEvidence {i+1}:")
    print(text[:400])

print("\nHallucination Confidence Score:", round(confidence,4))

if confidence > 0.75:
    print("Answer likely factual")

elif confidence > 0.5:
    print("Answer partially supported")

else:
    print("Potential hallucination detected")