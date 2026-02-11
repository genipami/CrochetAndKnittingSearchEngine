"""
Ingestion Script for Crochet & Knitting Search Engine
-------------------------------------------------------------

Features:
- Auto-creates index with correct keyword mappings for faceting
- Supports versioned index names via env var INDEX (default: patterns_v2)
- Handles PDF linking (local or via PDF_SERVED_PREFIX)
- Reports indexing stats clearly
- Re-running updates existing docs cleanly

Environment variables:
  ES_URL               - default http://localhost:9200
  INDEX                - default patterns_v2
  PDF_SERVED_PREFIX    - optional prefix: https://yourdomain/static/pdfs

Usage:
  python ingest_patterns.py --metadata ./metadata --pdfs ./pdfs
"""

import os
import json
import html
from pathlib import Path
from elasticsearch import Elasticsearch, helpers

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
INDEX = os.environ.get("INDEX", "patterns_v2")   # NEW VERSIONED INDEX
PDF_SERVED_PREFIX = os.environ.get("PDF_SERVED_PREFIX")  # optional


INDEX_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "text_en": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            },
            "normalizer": {
                "lc": { "type": "custom", "filter": ["lowercase"] }
            }
        }
    },
    "mappings": {
        "properties": {
            "id":            { "type": "long" },
            "name":          { "type": "text", "analyzer": "text_en",
                               "fields": { "raw": { "type": "keyword", "normalizer": "lc" } } },
            "permalink":     { "type": "keyword", "normalizer": "lc" },
            "url":           { "type": "keyword" },
            "external_url":  { "type": "keyword" },
            "download_url":  { "type": "keyword" },
            "designer_name": { "type": "keyword", "normalizer": "lc" },
            "project_type":  { "type": "keyword", "normalizer": "lc" },
            "fiber_art":     { "type": "keyword", "normalizer": "lc" },
            "yarn_weight":   { "type": "keyword", "normalizer": "lc" },

            "materials": {
                "type": "nested",
                "properties": {
                    "fiber": { "type": "keyword", "normalizer": "lc" },
                    "pct":   { "type": "float", "null_value": 0.0 }
                }
            },

            "stitches_used":   { "type": "keyword", "normalizer": "lc" },
            "techniques_used": { "type": "keyword", "normalizer": "lc" },

            "hook_sizes_mm":   { "type": "float" },
            "needle_sizes_mm": { "type": "float" },

            "published":       { "type": "date",
                                 "format": "yyyy/MM/dd||strict_date_optional_time||epoch_millis" },

            "sizes_available": { "type": "text", "analyzer": "text_en" },

            "rating_average":     { "type": "float" },
            "rating_count":       { "type": "integer" },
            "difficulty_average": { "type": "float" },
            "favorites_count":    { "type": "integer" },
            "projects_count":     { "type": "integer" },

            "pdf_path":  { "type": "keyword" },
            "best_link": { "type": "keyword" },
            "has_pdf":   { "type": "boolean" }
        }
    }
}

def served_url_for(pdf_path: Path) -> str:
    """Return HTTP-served URL if PDF_SERVED_PREFIX is set, else local path."""
    if not pdf_path:
        return None
    if PDF_SERVED_PREFIX:
        return f"{PDF_SERVED_PREFIX.rstrip('/')}/{pdf_path.name}"
    return str(pdf_path.resolve())


def normalize_url(u: str):
    if not u:
        return None
    return html.unescape(u).strip()


def compute_best_link(pdf_url, external_url, ravelry_url):
    """PDF > external > ravelry URL"""
    return pdf_url or external_url or ravelry_url


def doc_from_meta(meta: dict, pdf_dir: Path) -> dict:
    """Build final ES document"""
    pdf_path = None
    if meta.get("id") is not None:
        candidate = pdf_dir / f"{meta['id']}.pdf"
        if candidate.exists():
            pdf_path = candidate

    if pdf_path is None and meta.get("permalink"):
        candidate = pdf_dir / f"{meta['permalink']}.pdf"
        if candidate.exists():
            pdf_path = candidate

    ravelry_url = normalize_url(meta.get("url"))
    external_url = normalize_url(meta.get("external_url")) or normalize_url(meta.get("download_url"))
    download_url = normalize_url(meta.get("download_url"))

    pdf_url = served_url_for(pdf_path) if pdf_path else None
    best_link = compute_best_link(pdf_url, external_url, ravelry_url)

    return {
        "id": meta.get("id"),
        "name": meta.get("name"),
        "permalink": meta.get("permalink"),
        "url": ravelry_url,
        "external_url": external_url,
        "download_url": download_url,
        "designer_name": meta.get("designer_name"),
        "project_type": meta.get("project_type"),
        "fiber_art": meta.get("fiber_art"),
        "yarn_weight": meta.get("yarn_weight"),
        "materials": meta.get("materials") or [],
        "stitches_used": meta.get("stitches_used") or [],
        "techniques_used": meta.get("techniques_used") or [],
        "hook_sizes_mm": meta.get("hook_sizes_mm") or [],
        "needle_sizes_mm": meta.get("needle_sizes_mm") or [],
        "published": meta.get("published"),
        "sizes_available": meta.get("sizes_available"),
        "rating_average": meta.get("rating_average"),
        "rating_count": meta.get("rating_count"),
        "difficulty_average": meta.get("difficulty_average"),
        "favorites_count": meta.get("favorites_count"),
        "projects_count": meta.get("projects_count"),
        "has_pdf": bool(pdf_path),
        "pdf_path": str(pdf_path) if pdf_path else None,
        "best_link": best_link,
    }

def iter_actions(metadata_dir: Path, pdf_dir: Path):
    """Generator for bulk indexing"""
    for fp in sorted(Path(metadata_dir).glob("*.json")):
        with fp.open("r", encoding="utf-8") as f:
            try:
                meta = json.load(f)
            except Exception as e:
                print(f"[WARN] Skip malformed JSON: {fp} ({e})")
                continue

        doc = doc_from_meta(meta, pdf_dir)
        _id = str(meta.get("id") or meta.get("permalink"))
        if not _id:
            continue

        yield {
            "_op_type": "index",
            "_index": INDEX,
            "_id": _id,
            "_source": doc
        }



def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--pdfs", required=True, type=Path)
    ap.add_argument("--chunk", type=int, default=500)
    args = ap.parse_args()

    print(f"\nElasticsearch URL: {ES_URL}")
    print(f"Target index:       {INDEX}")

    es = Elasticsearch(ES_URL)

    if not es.indices.exists(index=INDEX):
        print(f"Index '{INDEX}' does NOT exist. Creating it...")
        es.indices.create(index=INDEX, body=INDEX_MAPPING)
        print("Index created.")
    else:
        print("Index already exists, continuing...")

    meta_files = list(Path(args.metadata).glob("*.json"))
    print(f"Found {len(meta_files)} metadata files for ingestion.")

    print("Starting bulk ingestion...")
    ok, errors = helpers.bulk(
        es,
        iter_actions(args.metadata, args.pdfs),
        stats_only=True,
        chunk_size=args.chunk,
        request_timeout=120
    )

    print("\nIngestion Summary")
    print(f"Indexed docs: {ok}")
    print(f"Errors:{errors}")

    try:
        count = es.count(index=INDEX)["count"]
        print(f"Index now contains {count} documents.")
    except Exception as e:
        print(f"[WARN] Could not retrieve index count: {e}")

    print("\nIngestion complete.\n")


if __name__ == "__main__":
    main()
