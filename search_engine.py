import faiss
import json
from spellchecker import SpellChecker
from clean_and_chunk import clean_text
from dictionaries import CUSTOM_WORDS
import numpy as np
from elasticsearch import Elasticsearch
from config import METADATA_DIR, model, ES_URL, ES_INDEX, EMBEDDINGS
from helpers import load_json_mappings, get_pattern_info, best_chunk_per_pattern, get_filters

spell = SpellChecker()
spell.word_frequency.load_words(CUSTOM_WORDS)

index = faiss.read_index("gte_base_ip.index")

def search_in_index(query: str, top_k=5):
    q_emb = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    S, I = index.search(q_emb, top_k)
    return S[0], I[0]

row_meta, pattern_to_rows = load_json_mappings()

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

    if fa := filters.get("fiber_art"):
        flt.append({"term": {"fiber_art": fa}})

    if yw := filters.get("yarn_weight"):
        flt.append({"term": {"yarn_weight": yw}})

    if tecs := filters.get("techniques_any"):
        flt.append({"terms": {"techniques_used": tecs}})

    if sts := filters.get("stitches_any"):
        flt.append({"terms": {"stitches_used": sts}})

    if mats := filters.get("materials_any"):
        flt.append({
            "nested": {
                "path": "materials",
                "query": {
                    "bool": { "filter": [ {"terms": {"materials.fiber": mats}} ] }
                }
            }
        })

    EPS = float(filters.get("size_tolerance_mm", 0.25))

    if (v := filters.get("hook_size_mm")) is not None:
        flt.append({"range": {"hook_sizes_mm": {"gte": float(v) - EPS, "lte": float(v) + EPS}}})

    if (v := filters.get("needle_size_mm")) is not None:
        flt.append({"range": {"needle_sizes_mm": {"gte": float(v) - EPS, "lte": float(v) + EPS}}})

    body = {
        "size": size,
        "_source": ["id"],
        "query": {"bool": {"filter": flt or [{"match_all": {}}]}},
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

def FAISS_and_print(initial_query: str, top_k: int = 5):
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

def hybrid_search(query: str,
                  filters: dict | None = None,
                  top_chunks: int = 500,
                  top_patterns: int = 5):
    print("Inside hybrid search")
    filters = filters or {}
    
    pattern_ids = es_filter_patterns(filters)
    

    if not pattern_ids:
        return []
    #print("Pattern ids", set(pattern_ids))

    cand_rows = rows_for_patterns(pattern_ids)
    if not cand_rows:
        return []
    #print("cand rows ids",  set(cand_rows))

    qv = embed_query(query)
    ranked_rows = score_subset_numpy(qv, cand_rows, top_k=top_chunks)
    #print("Len ranked ", ranked_rows)
    ranked_rows_fixed = []
    for row_idx, sim, pid in ranked_rows:
        if pid is None:
            continue
        ranked_rows_fixed.append((row_idx, sim, pid))

    collapsed = best_chunk_per_pattern(ranked_rows_fixed)

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

    print("\n--- Hybrid Results ---")

    for rank, r in enumerate(results, 1):
        print(f"{rank:>2}. pid={r['pattern_id']}  score={r['semantic_score']:.3f}  "
            f"src={r.get('chunk_source')} ord={r.get('chunk_order')}  "
            f"→ {r.get('best_link') or 'n/a'}  | {r.get('name')}")


def main():
    print("\n=== Crochet & Knitting Search ===")
    print("Press Ctrl+C to exit.\n")

    while True:
        initial_query = input("Query: ").strip()
        if not initial_query:
            continue

        mode = input("Mode [1=FAISS only, 2=Hybrid, 3=Elasticsearch]: ").strip()
        if mode == "1":
            FAISS_and_print(initial_query, top_k=5)
            continue

        filters = get_filters()

        if mode == "2":
            results = hybrid_search(initial_query, filters=filters, top_patterns=10)
            

        if mode == "3":
            pattern_ids = es_filter_patterns(filters, 5)

            print("\n--- Elasticsearch Results ---")
            for rank, pid in enumerate(pattern_ids, 1):
                pattern_path = METADATA_DIR / f"{pid}.json"
                pattern = json.loads(pattern_path.read_text(encoding="utf-8", errors="ignore"))

                link = (
                    pattern.get("url")
                    or pattern.get("ravelry_url")
                    or pattern.get("external_url")
                    or pattern.get("url")
                    or "n/a"
                )

                print(f"{rank:>2}. pid={pid} → {link} | {pattern.get('name')}")

        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")