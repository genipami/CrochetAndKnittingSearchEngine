
# -*- coding: utf-8 -*-
"""
Enrich patterns from Ravelry API using IDs from patterns_with_ids.txt:
- project_type (pattern_type/pattern_categories)
- fiber_art (craft)
- yarn_weight (normalized)
- materials (fiber breakdown via yarns)
- stitches_used (pattern_attributes + keyword scan)
- hook_sizes_mm / needle_sizes_mm (pattern_needle_sizes or gauge_description)
Saves JSON per pattern and appends to a CSV.
"""

import os
import re
import csv
import json
import time
import math
import pathlib
from collections import defaultdict
import requests

from requests_oauthlib import OAuth1

CONSUMER_KEY = "15c948c58a84cc81c3cd01df60d40a28"
CONSUMER_SECRET = "uqlkk_iRsKsluJHDEyJABKcLsutsxupvWjduE38M"
ACCESS_TOKEN = "6qCZndZUP1cHXUPgpWx1nn7ZNpe5cyz48WJQeygZ"
ACCESS_SECRET = "hkBOYFw9c4fuKoF976XAuFi99Puu5xcAxbCGqXSP"

AUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

r = requests.get("https://api.ravelry.com/patterns/7492852.json", auth=AUTH)
print(r.status_code, r.json())


BASE = "https://api.ravelry.com"
DETAIL_URL = f"{BASE}/patterns/{{id}}.json"
YARNS_SINGLE_URL = f"{BASE}/yarns/{{id}}.json"
YARNS_BATCH_URL = f"{BASE}/yarns.json"  # optional batch

INPUT_FILE = "patterns_with_ids.txt"
OUT_DIR = pathlib.Path("downloads_api_enriched")
OUT_DIR.mkdir(exist_ok=True)
CSV_PATH = OUT_DIR / "metadata_enriched.csv"

DETAIL_TIMEOUT = 30
YARN_TIMEOUT = 30
PAUSE_DETAIL = 0.4
PAUSE_YARN = 0.3

# ----------------------------
# Helpers
# ----------------------------
def read_ids_file(path):
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                try:
                    pid = int(parts[0])
                    permalink = parts[1]
                    pairs.append((pid, permalink))
                except ValueError:
                    continue
    return pairs

def fetch_pattern_details(pid: int) -> dict | None:
    url = DETAIL_URL.format(id=pid)
    r = requests.get(url, auth=AUTH, timeout=DETAIL_TIMEOUT)
    if r.status_code == 200:
        return r.json().get("pattern") or r.json()
    print(f"[WARN] details failed for id {pid}: {r.status_code}")
    return None

# Normalization helpers
WEIGHT_ALIASES = {
    "lace": "Lace", "thread": "Lace", "cobweb": "Lace",
    "fingering": "Fingering", "sock": "Fingering",
    "sport": "Sport",
    "dk": "DK", "double knit": "DK",
    "worsted": "Worsted", "aran": "Aran",
    "bulky": "Bulky", "chunky": "Bulky",
    "super bulky": "Super Bulky", "jumbo": "Super Bulky",
}

def normalize_weight(text):
    if not text:
        return None
    t = text.lower()
    for k, v in WEIGHT_ALIASES.items():
        if k in t:
            return v
    return text.strip()

def extract_project_type(p):
    ptype = (p.get("pattern_type") or {}).get("name")
    if ptype:
        return ptype
    cats = p.get("pattern_categories") or []
    best = None
    for c in cats:
        nm = c.get("name")
        depth = 0
        parent = c.get("parent")
        while isinstance(parent, dict):
            depth += 1
            parent = parent.get("parent")
        if nm and (best is None or depth > best[0]):
            best = (depth, nm)
    return best[1] if best else None

def extract_fiber_art(p):
    craft = p.get("craft")
    if isinstance(craft, dict):
        return craft.get("name")
    if isinstance(craft, list) and craft:
        return craft[0].get("name")
    return None

def extract_weight(p):
    w = p.get("yarn_weight_description")
    if w:
        return normalize_weight(w)
    yw = p.get("yarn_weight")
    if isinstance(yw, list) and yw:
        return normalize_weight(yw[0].get("name"))
    if isinstance(yw, dict) and yw.get("name"):
        return normalize_weight(yw["name"])
    return None

def extract_stitches(p):
    attrs = set()
    for key in ("pattern_attributes", "personal_attributes"):
        val = p.get(key)
        if isinstance(val, list):
            for a in val:
                if isinstance(a, dict) and a.get("name"):
                    attrs.add(a["name"].strip())
                elif isinstance(a, str):
                    attrs.add(a.strip())
    return sorted(attrs)

def extract_sizes_mm(p):
    needles_mm, hooks_mm = [], []
    pns = p.get("pattern_needle_sizes")
    if isinstance(pns, list):
        for item in pns:
            metric = None
            for key in ("metric", "mm", "metric_size"):
                if isinstance(item, dict) and item.get(key):
                    metric = item.get(key)
                    break
            if isinstance(metric, str):
                try:
                    metric = float(metric.replace(",", "."))
                except:
                    metric = None
            if isinstance(metric, (int, float)):
                if "hook" in str(item).lower():
                    hooks_mm.append(round(metric, 2))
                else:
                    needles_mm.append(round(metric, 2))
    # Fallback: parse gauge_description
    if not hooks_mm and not needles_mm:
        gd = (p.get("gauge_description") or "") + " " + (p.get("gauge") or "")
        for mm in re.findall(r"(\d+(?:\.\d+)?)\s*mm", gd.lower()):
            val = round(float(mm), 2)
            if "crochet" in (extract_fiber_art(p) or "").lower():
                hooks_mm.append(val)
            else:
                needles_mm.append(val)
    return sorted(set(hooks_mm)), sorted(set(needles_mm))

def collect_yarn_ids(p):
    ids = set()
    for pack in p.get("packs") or []:
        yid = pack.get("yarn_id") or (pack.get("yarn") or {}).get("id")
        if isinstance(yid, int):
            ids.add(yid)
    return list(ids)

def fetch_yarn_details(yarn_ids):
    details = []
    for yid in yarn_ids:
        url = YARNS_SINGLE_URL.format(id=yid)
        r = requests.get(url, auth=AUTH, timeout=YARN_TIMEOUT)
        if r.status_code == 200:
            y = r.json().get("yarn") or r.json()
            details.append(y)
        time.sleep(PAUSE_YARN)
    return details

def extract_materials(yarns):
    tally = defaultdict(float)
    for y in yarns:
        fibers = y.get("fibers") or []
        for f in fibers:
            name = f.get("name")
            pct = f.get("pct") or f.get("percentage") or f.get("percent")
            if name:
                try:
                    tally[name.strip()] += float(pct) if pct else 0.0
                except:
                    tally[name.strip()] += 0.0
    total = sum(tally.values())
    out = []
    if total > 0:
        for name, val in sorted(tally.items(), key=lambda kv: -kv[1]):
            out.append({"fiber": name, "pct": round(100.0 * val / total, 1)})
    else:
        for name in tally.keys():
            out.append({"fiber": name, "pct": None})
    return out

def save_json(obj, slug):
    path = OUT_DIR / f"{slug}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path

def append_csv(rows):
    flat = []
    for r in rows:
        rr = dict(r)
        mats = rr.pop("materials", [])
        rr["materials"] = "; ".join(f"{m['fiber']}:{m.get('pct','')}" for m in mats)
        for key in ("stitches_used", "hook_sizes_mm", "needle_sizes_mm"):
            rr[key] = "; ".join(str(x) for x in rr.get(key, []))
        flat.append(rr)
    fieldnames = sorted({k for r in flat for k in r.keys()})
    write_header = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        for r in flat:
            w.writerow(r)

# ----------------------------
# Main
# ----------------------------
def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] {INPUT_FILE} not found.")
        return

    pairs = read_ids_file(INPUT_FILE)
    print(f"[INFO] Loaded {len(pairs)} patterns from {INPUT_FILE}")

    output_rows = []

    for i, (pid, permalink) in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] Fetching ID {pid} ({permalink})")
        p = fetch_pattern_details(pid)
        time.sleep(PAUSE_DETAIL)
        if not p:
            continue

        project_type = extract_project_type(p)
        fiber_art = extract_fiber_art(p)
        yarn_weight = extract_weight(p)
        stitches_used = extract_stitches(p)
        hook_sizes_mm, needle_sizes_mm = extract_sizes_mm(p)

        yarn_ids = collect_yarn_ids(p)
        yarns = fetch_yarn_details(yarn_ids) if yarn_ids else []
        materials = extract_materials(yarns)

        enriched = {
            "id": pid,
            "name": p.get("name"),
            "permalink": permalink,
            "url": p.get("url"),
            "designer_name": (p.get("designer") or {}).get("name"),
            "project_type": project_type,
            "fiber_art": fiber_art,
            "yarn_weight": yarn_weight,
            "materials": materials,
            "stitches_used": stitches_used,
            "hook_sizes_mm": hook_sizes_mm,
            "needle_sizes_mm": needle_sizes_mm,
            "published": p.get("published"),
            "sizes_available": p.get("sizes_available"),
            "rating_average": p.get("rating_average"),
            "rating_count": p.get("rating_count"),
            "difficulty_average": p.get("difficulty_average"),
            "favorites_count": p.get("favorites_count"),
            "projects_count": p.get("projects_count"),
        }

        save_json(enriched, permalink)
        output_rows.append(enriched)

    if output_rows:
        append_csv(output_rows)
        print(f"[INFO] Wrote {len(output_rows)} records to {CSV_PATH}")
    else:
        print("[INFO] No records written.")

if __name__ == "__main__":
    main()

