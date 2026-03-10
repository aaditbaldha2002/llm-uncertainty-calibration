from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np

# Load knowledge base
kb_df = pd.read_csv("data/knowledge_base.csv")
texts = kb_df['text'].tolist()

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner product = cosine similarity
index.add(embeddings)

# Save index and texts for later
faiss.write_index(index, "kb_index.faiss")
kb_df.to_pickle("kb_texts.pkl")

print(f"FAISS index created with {len(texts)} entries.")