import pandas as pd
kb_files = ["data/squad_train.csv", "data/squad_v2.csv", "data/hotpotqa.csv", "data/hotpotqa_test.csv", "data/truthfulqa_kb.csv"]
dfs = [pd.read_csv(f) for f in kb_files]
combined = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=['text'])
combined.to_csv("data/knowledge_base.csv", index=False, encoding="utf-8")