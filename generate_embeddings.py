from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from huggingface_hub import login
import os

HF_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
try:
    login(token=HF_token)
except:
    print("[ERROR] Loging failed!")    

ROOT_DIR = Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"
TXT_DIR = ROOT_DIR / "txts"
CHUNK_DIR = ROOT_DIR / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)



device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("thenlper/gte-base", device=device)


def load_chunks(folder: str) -> list[str]:
    chunks = []
    i = 0
    for p in Path(folder).glob("*.json"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        chunks.append(text)
        i = i+1
        print(f"[INFO]{i}th chunk loaded.")
    print("Loaded chunks!") 
    return chunks   

all_chunks = load_chunks(CHUNK_DIR)

embeddings = model.encode(
    all_chunks,
    batch_size=64,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)

np.save("embeddings_gte_base.npy", embeddings)
with open("chunks_index.txt", "w", encoding="utf-8") as f:
    for ch in all_chunks:
        f.write(ch.replace("\n", " ") + "\n")

print("Saved embeddings_gte_base.npy and chunks_index.txt")