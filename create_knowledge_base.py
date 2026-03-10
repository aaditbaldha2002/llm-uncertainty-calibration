import json
import pandas as pd

# Load the JSON file
with open("data/hotpot_dev_fullwiki_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
sources = []

for entry in data:
    # Add the main answer
    answer = entry.get("answer", "")
    if answer:
        texts.append(answer)
        sources.append("hotpotqa")

    # Add all context paragraphs
    for ctx_item in entry.get("context", []):
        # ctx_item = [title, list_of_paragraphs]
        if len(ctx_item) != 2:
            continue
        paragraphs = ctx_item[1]
        for para in paragraphs:
            texts.append(para)
            sources.append("hotpotqa")

# Create a DataFrame
df = pd.DataFrame({
    "text": texts,
    "source": sources
})

# Save to CSV
df.to_csv("data/hotpotqa.csv", index=False, encoding="utf-8")
print(f"Converted {len(df)} text chunks to CSV")

# Load HotpotQA test JSON
with open("data/hotpot_test_fullwiki_v1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
sources = []

for entry in data:
    # Add the main answer
    answer = entry.get("answer", "")
    if answer:
        texts.append(answer)
        sources.append("hotpotqa_test")

    # Add all context paragraphs
    for ctx_item in entry.get("context", []):
        # ctx_item = [title, list_of_paragraphs]
        if len(ctx_item) != 2:
            continue
        paragraphs = ctx_item[1]
        for para in paragraphs:
            texts.append(para)
            sources.append("hotpotqa_test")

# Create DataFrame
df = pd.DataFrame({
    "text": texts,
    "source": sources
})

# Save to CSV
df.to_csv("data/hotpotqa_test.csv", index=False, encoding="utf-8")
print(f"Converted {len(df)} text chunks to CSV")

# Load SQuAD-style JSON
with open("data/dev-v2.0.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
sources = []

for article in data["data"]:
    title = article.get("title", "unknown")
    for para in article.get("paragraphs", []):
        context = para.get("context", "")
        if context:
            texts.append(context)
            sources.append(title)  # Use title as the source

# Create DataFrame
df = pd.DataFrame({
    "text": texts,
    "source": sources
})

# Save to CSV
df.to_csv("data/squad_v2.csv", index=False, encoding="utf-8")
print(f"Converted {len(df)} context paragraphs to CSV")

import json
import pandas as pd

# Load train JSON
with open("data/train-v2.0.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []
sources = []

for article in data["data"]:
    title = article.get("title", "unknown")
    for para in article.get("paragraphs", []):
        context = para.get("context", "")
        if context:
            texts.append(context)
            sources.append(title)  # Use title as the source

# Create DataFrame
df = pd.DataFrame({
    "text": texts,
    "source": sources
})

# Save to CSV
df.to_csv("data/squad_train.csv", index=False, encoding="utf-8")
print(f"Converted {len(df)} context paragraphs to CSV")

# Load TruthfulQA CSV
df = pd.read_csv("data/TruthfulQA.csv")

texts = []
sources = []

# Add Best Answer
for idx, row in df.iterrows():
    best_answer = str(row['Best Answer']).strip()
    if best_answer:
        texts.append(best_answer)
        sources.append(row.get('Source', 'truthfulqa'))

    # Optionally add all correct answers if available
    correct_answers = str(row.get('Correct Answers', '')).strip()
    if correct_answers:
        # Split by comma or semicolon if multiple answers are in a string
        for ans in correct_answers.split(','):
            ans = ans.strip()
            if ans and ans != best_answer:  # avoid duplicates
                texts.append(ans)
                sources.append(row.get('Source', 'truthfulqa'))

# Create DataFrame
kb_df = pd.DataFrame({
    "text": texts,
    "source": sources
})

# Save to CSV
kb_df.to_csv("data/truthfulqa_kb.csv", index=False, encoding="utf-8")
print(f"Converted {len(kb_df)} TruthfulQA answers to CSV")