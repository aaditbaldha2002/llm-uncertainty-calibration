import pandas as pd
import numpy as np
from hallucination_engine import retrieve_and_verify_batch
import json

# ── Config ────────────────────────────────────────────────
DATASET_PATH = "data/TruthfulQA.csv"
SAMPLE_SIZE = 100          # Set to None to run full 790
CONFIDENCE_THRESHOLD = 0.8 # Above = factual, below = hallucination
RANDOM_SEED = 42

# ── Load dataset ──────────────────────────────────────────
df = pd.read_csv(DATASET_PATH)

# Drop rows with missing values in required columns
df = df.dropna(subset=["Question", "Best Answer", "Best Incorrect Answer"])

# Sample for speed — set SAMPLE_SIZE = None for full eval
if SAMPLE_SIZE:
    df = df.sample(n=SAMPLE_SIZE, random_state=RANDOM_SEED).reset_index(drop=True)

print(f"Running benchmark on {len(df)} questions...")
print("-" * 50)

# ── Run evaluation ────────────────────────────────────────
results = []

for idx, row in df.iterrows():
    question = row["Question"]
    correct_answer = row["Best Answer"]
    incorrect_answer = row["Best Incorrect Answer"]

    try:
        # Score correct answer
        correct_result = retrieve_and_verify_batch(question, correct_answer)
        correct_confidence = correct_result["final_confidence"]

        # Score incorrect answer
        incorrect_result = retrieve_and_verify_batch(question, incorrect_answer)
        incorrect_confidence = incorrect_result["final_confidence"]

        # Predictions based on threshold
        correct_prediction = "factual" if correct_confidence >= CONFIDENCE_THRESHOLD else "hallucination"
        incorrect_prediction = "factual" if incorrect_confidence >= CONFIDENCE_THRESHOLD else "hallucination"

        # True positives: correct answer scored as factual
        # True negatives: incorrect answer scored as hallucination
        correct_tp = correct_prediction == "factual"
        incorrect_tn = incorrect_prediction == "hallucination"

        results.append({
            "question": question,
            "correct_answer": correct_answer,
            "incorrect_answer": incorrect_answer,
            "correct_confidence": round(correct_confidence, 4),
            "incorrect_confidence": round(incorrect_confidence, 4),
            "correct_detected": correct_tp,
            "hallucination_detected": incorrect_tn,
        })

        # Progress log every 10 rows
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(df)} questions...")

    except Exception as e:
        print(f"  [ERROR] Row {idx}: {e}")
        continue

# ── Compute metrics ───────────────────────────────────────
results_df = pd.DataFrame(results)

total = len(results_df)
correct_answers_scores = results_df["correct_confidence"].tolist()
incorrect_answers_scores = results_df["incorrect_confidence"].tolist()

# Accuracy on correct answers (should score >= threshold)
factual_accuracy = results_df["correct_detected"].sum() / total * 100

# Accuracy on incorrect answers (should score < threshold)
hallucination_detection_rate = results_df["hallucination_detected"].sum() / total * 100

# Overall accuracy (both correct at same time)
both_correct = (results_df["correct_detected"] & results_df["hallucination_detected"]).sum()
overall_accuracy = both_correct / total * 100

# Average confidence scores
avg_correct_conf = np.mean(correct_answers_scores)
avg_incorrect_conf = np.mean(incorrect_answers_scores)

# Separation gap (higher = better discrimination)
separation_gap = avg_correct_conf - avg_incorrect_conf

# ── Print results ─────────────────────────────────────────
print("\n" + "=" * 50)
print("BENCHMARK RESULTS — TruthfulQA")
print("=" * 50)
print(f"Sample size:                  {total} questions")
print(f"Confidence threshold:         {CONFIDENCE_THRESHOLD}")
print("-" * 50)
print(f"Factual answer detection:     {factual_accuracy:.1f}%")
print(f"  (correct answers scoring >= {CONFIDENCE_THRESHOLD})")
print(f"Hallucination detection rate: {hallucination_detection_rate:.1f}%")
print(f"  (incorrect answers scoring < {CONFIDENCE_THRESHOLD})")
print(f"Overall accuracy:             {overall_accuracy:.1f}%")
print(f"  (both correct simultaneously)")
print("-" * 50)
print(f"Avg confidence (factual):     {avg_correct_conf:.4f}")
print(f"Avg confidence (hallucination): {avg_incorrect_conf:.4f}")
print(f"Separation gap:               {separation_gap:.4f}")
print("=" * 50)

# ── Save detailed results ─────────────────────────────────
results_df.to_csv("benchmark_results.csv", index=False)
print(f"\nDetailed results saved to benchmark_results.csv")

# ── Save summary as JSON for README ──────────────────────
summary = {
    "dataset": "TruthfulQA",
    "sample_size": total,
    "confidence_threshold": CONFIDENCE_THRESHOLD,
    "factual_accuracy": round(factual_accuracy, 1),
    "hallucination_detection_rate": round(hallucination_detection_rate, 1),
    "overall_accuracy": round(overall_accuracy, 1),
    "avg_confidence_factual": round(float(avg_correct_conf), 4),
    "avg_confidence_hallucination": round(float(avg_incorrect_conf), 4),
    "separation_gap": round(float(separation_gap), 4),
}
with open("benchmark_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("Summary saved to benchmark_summary.json")