import pathlib
from sentence_transformers import SentenceTransformer
import torch
import os
import numpy as np

ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"

RESULTS_FILE = "all_query_results.csv"

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("thenlper/gte-base", device=device)

EMB_PATH = "embeddings_gte_base.npy"
EMBEDDINGS = np.load(EMB_PATH, mmap_mode="r")

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
ES_INDEX = os.environ.get("INDEX", "patterns_v3")