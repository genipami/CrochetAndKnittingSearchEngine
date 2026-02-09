import faiss
import numpy as np

def create_index():
    # Load previously saved arrays
    emb = np.load("embeddings_gte_base.npy").astype("float32")  # FAISS prefers float32
    dim = emb.shape[1]

    # Cosine similarity with normalized vectors is equivalent to inner product
    index = faiss.IndexFlatIP(dim)
    index.add(emb)  # add all vectors to the index

    faiss.write_index(index, "gte_base_ip.index")
    print("FAISS index saved.")