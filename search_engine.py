import faiss
from sentence_transformers import SentenceTransformer
import torch
import json
import pathlib
from spellchecker import SpellChecker
import csv
from clean_and_chunk import clean_text
from dictionaries import CUSTOM_WORDS, QUERY_SETS
from pathlib import Path
import os
import numpy as np
from elasticsearch import Elasticsearch
from testing import get_int

spell = SpellChecker()
spell.word_frequency.load_words(CUSTOM_WORDS)

ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"

RESULTS_FILE = "all_query_results.csv"

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("thenlper/gte-base", device=device)

index = faiss.read_index("gte_base_ip.index")

def search_in_index(query: str, top_k=5):
    q_emb = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    S, I = index.search(q_emb, top_k)  # S = similarity scores, I = indices
    return S[0], I[0]

def load_json_mappings(row_meta_path="row_meta.json", pattern_to_rows_path="pattern_to_rows.json"):
    if not Path(row_meta_path).exists() or not Path(pattern_to_rows_path).exists():
        print("[WARN] row_meta.json / pattern_to_rows.json not found. "
              "Run create_chunk_mapping.py first. Falling back to legacy mapping if available.")
        return {}, {}

    with open(row_meta_path, "r", encoding="utf-8") as f:
        rm = {int(k): v for k, v in json.load(f).items()}
    with open(pattern_to_rows_path, "r", encoding="utf-8") as f:
        ptr = {int(k): v for k, v in json.load(f).items()}
    return rm, ptr

row_meta, pattern_to_rows = load_json_mappings()


# =============================================================================
# --- ADDED: Load embeddings.npy as memmap for fast subset scoring (no re-embedding)
#            If not present, we’ll still be able to run global FAISS and post-filter via ES.
# =============================================================================
EMB_PATH = "embeddings_gte_base.npy"
EMBEDDINGS = np.load(EMB_PATH, mmap_mode="r")

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
ES_INDEX = os.environ.get("INDEX", "patterns_v3")

def es_client():
    try:
        return Elasticsearch(ES_URL)
    except Exception as e:
        print(f"[WARN] Could not connect to Elasticsearch at {ES_URL}: {e}")
        return None

def es_filter_patterns(filters: dict, size=500):

    es = es_client()
    if es is None:
        return []

    flt = []
    if filters.get("fiber_art"):
        flt.append({"term": {"fiber_art": filters["fiber_art"]}})
    if filters.get("yarn_weight"):
        flt.append({"term": {"yarn_weight": filters["yarn_weight"]}})
    if filters.get("stitches_any"):
        flt.append({"terms": {"stitches_used": filters["stitches_any"]}})
    if filters.get("has_pdf") is not None:
        flt.append({"term": {"has_pdf": bool(filters["has_pdf"])}})
    if filters.get("published_from"):
        flt.append({"range": {"published": {"gte": filters["published_from"]}}})

    body = {
        "size": size,
        "_source": ["id"],
        "query": {"bool": {"filter": flt or [{"match_all": {}}]}}
    }

    try:
        res = es.search(index=ES_INDEX, body=body)
        return [int(h["_source"]["id"]) for h in res["hits"]["hits"] if "id" in h["_source"]]
    except Exception as e:
        print(f"[WARN] ES query failed: {e}")
        return []

def embed_query(q: str) -> np.ndarray:
    return model.encode([q], normalize_embeddings=True, convert_to_numpy=True)[0].astype("float32")

def rows_for_patterns(pattern_ids: list[int]) -> list[int]:
    rows: list[int] = []
    for pattern_id in pattern_ids:
        rows.extend(pattern_to_rows.get(pattern_id, []))
    return rows

def score_subset_numpy(q_vec: np.ndarray, row_indices: list[int], top_k: int = 100):
    if EMBEDDINGS is None or not row_indices:
        return []

    cand = EMBEDDINGS[row_indices]             
    sims = cand @ q_vec               

    if top_k < len(row_indices):
        top_local = np.argpartition(-sims, top_k)[:top_k]
        top_local = top_local[np.argsort(-sims[top_local])]
    else:
        top_local = np.argsort(-sims)

    ranked = [(row_indices[li], float(sims[li]), row_meta.get(row_indices[li], {}).get("pattern_id")) for li in top_local]
    return ranked

def best_chunk_per_pattern(ranked_rows):
    best = {}
    for row_idx, sim, pattern_id in ranked_rows:
        if pattern_id is None:
            continue
        if (pattern_id not in best) or (sim > best[pattern_id]["sim"]):
            best[pattern_id] = {"row_idx": row_idx, "sim": sim}
    return sorted(((pattern_id, d["row_idx"], d["sim"]) for pid, d in best.items()), key=lambda x: -x[2])


def query_and_print(initial_query: str, top_k: int = 5):
    """Original FAISS-only path (kept)."""
    spell_corrected_query = " ".join(spell.correction(w) for w in initial_query.split())
    query = clean_text(spell_corrected_query)

    scores, idxs = search_in_index(query, top_k)

    for rank, (score, idx) in enumerate(zip(scores, idxs), 1):
        pattern_id = row_meta.get(int(idx), {}).get("pattern_id")
        source = row_meta.get(int(idx), {}).get("source")
        order = row_meta.get(int(idx), {}).get("order")

        files = list(METADATA_DIR.glob(f"{pattern_id}.json")) if pattern_id is not None else []
        pattern_link = None
        if files:
            with open(files[0], "r", encoding="utf-8") as jf:
                js = json.load(jf)
                pattern_link = js.get("best_link") or js.get("url") or js.get("external_url") or "PDF only!"
        else:
            pattern_link = "PDF only!"

        print(f"{rank:>2}  score={score:.4f}  pid={pattern_id}  src={source}  ord={order}  → {pattern_link}")


def get_pattern_info(pattern_id: int) -> dict:
    p = METADATA_DIR / f"{pattern_id}.json"
    return json.load(open(p, "r", encoding="utf-8"))        

def hybrid_search(query: str,
                  filters: dict | None = None,
                  top_candidates: int = 400,
                  top_chunks: int = 200,
                  top_patterns: int = 10):

    filters = filters or {}
    
    pattern_ids = es_filter_patterns(filters, size=top_candidates)
    

    cand_rows = rows_for_patterns(pattern_ids)
    if not cand_rows:
        return []

    qv = embed_query(query)
    ranked_rows = score_subset_numpy(qv, cand_rows, top_k=top_chunks)
    collapsed = best_chunk_per_pattern(ranked_rows)

    results = []
    for pid, row_idx, sim in collapsed[:top_patterns]:
        m = row_meta.get(row_idx, {})
        pinfo = get_pattern_info(pid)
        results.append({
            "pattern_id": pid,
            "name": pinfo.get("name"),
            "best_link": pinfo.get("best_link") or pinfo.get("url") or pinfo.get("external_url"),
            "semantic_score": float(sim),
            "chunk_row": row_idx,
            "chunk_source": m.get("source"),
            "chunk_order": m.get("order"),
            "filename": m.get("filename"),
        })
        return results

def main():
    print("\n=== Crochet & Knitting Search ===")
    print("Type your query and choose:")
    print("  1) FAISS only (legacy)")
    print("  2) Hybrid (Elasticsearch filters + semantic rerank)")
    print("Press Ctrl+C to exit.\n")

    while True:
        initial_query = input("Query: ").strip()
        if not initial_query:
            continue

        mode = input("Mode [1=FAISS only, 2=Hybrid]: ").strip()
        if mode == "1":
            query_and_print(initial_query, top_k=10)
            continue

        filters = {}
        fa = input("Filter fiber_art (e.g., crochet/knitting) or blank: ").strip()
        if fa:
            filters["fiber_art"] = fa

        yw = input("Filter yarn_weight (e.g., worsted, super bulky) or blank: ").strip()
        if yw:
            filters["yarn_weight"] = yw

        has_pdf = input("Filter has_pdf? [y/N]: ").strip().lower()
        if has_pdf in ("y", "yes", "true", "1"):
            filters["has_pdf"] = True

        results = hybrid_search(initial_query, filters=filters, top_patterns=10, boost_notes=1.0)
        print("\n--- Hybrid Results ---")
        for rank, r in enumerate(results, 1):
            print(f"{rank:>2}. pid={r['pattern_id']}  score={r['semantic_score']:.3f}  "
                  f"src={r.get('chunk_source')} ord={r.get('chunk_order')}  "
                  f"→ {r.get('best_link') or 'n/a'}  | {r.get('name')}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")