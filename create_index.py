import faiss
import numpy as np

def create_index():
    emb = np.load("embeddings_gte_base.npy").astype("float32")
    dim = emb.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    faiss.write_index(index, "gte_base_ip.index")
    print("FAISS index saved.")