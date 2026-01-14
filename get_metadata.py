# -*- coding: utf-8 -*-
"""
Enrich patterns from Ravelry API using IDs from patterns_with_ids.txt

Collected fields:
- project_type (pattern_type/pattern_categories)
- fiber_art (craft)
- yarn_weight (normalized)
- materials (fiber breakdown via yarn IDs with robust fiber parsing; fallback to yarn names)
- stitches_used (stitch keywords only)
- techniques_used (separate from stitches; from attributes + keyword scan)
- hook_sizes_mm / needle_sizes_mm (pattern_needle_sizes with US->mm fallback, plus gauge_description)
- designer_name (pattern_author/designers)
- canonical Ravelry URL + external URL (source)
- free_ravelry_download + download_url

Outputs:
- JSON per pattern in downloads_api_enriched/
- Appends flattened rows to downloads_api_enriched/metadata_enriched.csv
"""

import os
import re
import csv
import json
import time
import pathlib
from collections import defaultdict
from typing import Optional, Tuple, List, Dict, Any

import requests
from requests_oauthlib import OAuth1

# -----------------------------------
# Auth (prefer environment variables)
# -----------------------------------
CONSUMER_KEY = os.getenv("RAVELRY_CONSUMER_KEY", "15c948c58a84cc81c3cd01df60d40a28")
CONSUMER_SECRET = os.getenv("RAVELRY_CONSUMER_SECRET", "uqlkk_iRsKsluJHDEyJABKcLsutsxupvWjduE38M")
ACCESS_TOKEN = os.getenv("RAVELRY_ACCESS_TOKEN", "6qCZndZUP1cHXUPgpWx1nn7ZNpe5cyz48WJQeygZ")
ACCESS_SECRET = os.getenv("RAVELRY_ACCESS_SECRET", "hkBOYFw9c4fuKoF976XAuFi99Puu5xcAxbCGqXSP")

AUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

BASE = "https://api.ravelry.com"
DETAIL_URL = (
    f"{BASE}/patterns/{{id}}.json"
    "?include=pattern_author,designers,packs,yarns,pattern_attributes,"
    "craft,pattern_categories,pattern_type,pattern_needle_sizes,yarn_weight"
)
YARN_URL = f"{BASE}/yarns/{{id}}.json"

INPUT_FILE = "patterns_with_ids.txt"
OUT_DIR = pathlib.Path("metadata")
OUT_DIR.mkdir(exist_ok=True)
CSV_PATH = OUT_DIR / "metadata_enriched.csv"

DETAIL_TIMEOUT = 30
YARN_TIMEOUT = 30
PAUSE_DETAIL = 0.35
PAUSE_YARN = 0.25


# ---------------------------
# Utilities
# ---------------------------
def read_ids_file(path: str) -> List[Tuple[int, str]]:
    pairs: List[Tuple[int, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(",")]
            if len(parts) >= 2:
                try:
                    pid = int(parts[0])
                except ValueError:
                    continue
                permalink = parts[1]
                pairs.append((pid, permalink))
    return pairs


def fetch_pattern_details(pid: int) -> Optional[Dict[str, Any]]:
    url = DETAIL_URL.format(id=pid)
    try:
        r = requests.get(url, auth=AUTH, timeout=DETAIL_TIMEOUT)
    except requests.RequestException as e:
        print(f"[WARN] details exception for id {pid}: {e}")
        return None
    if r.status_code == 200:
        return r.json().get("pattern") or r.json()
    print(f"[WARN] details failed for id {pid}: {r.status_code}")
    return None


# ---------------------------
# Normalization helpers
# ---------------------------
WEIGHT_ALIASES = {
    "lace": "Lace", "thread": "Lace", "cobweb": "Lace",
    "fingering": "Fingering", "sock": "Fingering",
    "sport": "Sport",
    "dk": "DK", "double knit": "DK",
    "worsted": "Worsted", "aran": "Aran",
    "bulky": "Bulky", "chunky": "Bulky",
    "super bulky": "Super Bulky", "jumbo": "Super Bulky",
}


def normalize_weight(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    t = str(text).lower()
    for k, v in WEIGHT_ALIASES.items():
        if k in t:
            return v
    return str(text).strip()


def extract_project_type(p: Dict[str, Any]) -> Optional[str]:
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


def extract_fiber_art(p: Dict[str, Any]) -> Optional[str]:
    craft = p.get("craft")
    if isinstance(craft, dict):
        return craft.get("name")
    if isinstance(craft, list) and craft:
        return craft[0].get("name")
    return None


def extract_weight(p: Dict[str, Any]) -> Optional[str]:
    w = p.get("yarn_weight_description")
    if w:
        return normalize_weight(w)
    yw = p.get("yarn_weight")
    if isinstance(yw, list) and yw:
        return normalize_weight(yw[0].get("name"))
    if isinstance(yw, dict) and yw.get("name"):
        return normalize_weight(yw["name"])
    return None


# ---------------------------
# Stitches vs Techniques
# ---------------------------
# Keep stitches focused on stitch types, not techniques.
STITCH_KEYWORDS = {
    "single crochet": "Single crochet (sc)",
    "sc": "Single crochet (sc)",
    "half double crochet": "Half double crochet (hdc)",
    "hdc": "Half double crochet (hdc)",
    "double crochet": "Double crochet (dc)",
    "dc": "Double crochet (dc)",
    "treble crochet": "Treble crochet (tr)",
    "tr": "Treble crochet (tr)",
    "slip stitch": "Slip stitch (sl st)",
    "sl st": "Slip stitch (sl st)",
    "shell": "Shell",
    "v-stitch": "V-stitch",
    "granny": "Granny",
    "moss stitch": "Moss/Linen stitch",
    "linen stitch": "Moss/Linen stitch",
    "puff": "Puff stitch",
    "bobble": "Bobble",
    "popcorn": "Popcorn",
    "waffle": "Waffle",
    "star stitch": "Star stitch",
    "c2c": "C2C",  # sometimes referenced as a stitch; also treated as technique below
    "corner to corner": "C2C",
    "filet": "Filet crochet",
}


def extract_stitches(p: Dict[str, Any]) -> List[str]:
    # Stitches from keyword scan only (to avoid conflating attributes like 'mosaic'/'in-the-round')
    hay = " ".join([
        str(p.get("name") or ""),
        str(p.get("notes") or ""),
        str(p.get("notes_html") or ""),
        str(p.get("gauge_description") or ""),
    ]).lower()
    out = set()
    for kw, label in STITCH_KEYWORDS.items():
        if kw in hay:
            out.add(label)
    return sorted(out)


TECHNIQUE_ATTRS = {
    # construction / shaping
    "in-the-round": "In the round",
    "flat": "Worked flat",
    "top-down": "Top-down",
    "bottom-up": "Bottom-up",
    "seamed": "Seamed",
    "seamless": "Seamless",
    "modular": "Modular",
    "join-as-you-go": "Join-as-you-go",
    "c2c": "C2C",
    "corner-to-corner": "C2C",

    # colorwork / texture techniques
    "colorwork": "Colorwork",
    "fair-isle": "Fair Isle",
    "stranded": "Stranded colorwork",
    "intarsia": "Intarsia",
    "brioche": "Brioche",
    "mosaic": "Mosaic",
    "tapestry-crochet": "Tapestry crochet",
    "filet": "Filet crochet",
    "overlay-crochet": "Overlay crochet",
    "entrelac": "Entrelac",

    # charts & direction
    "chart": "Charted",
}

TECHNIQUE_KEYWORDS = {
    "in the round": "In the round",
    "worked flat": "Worked flat",
    "top-down": "Top-down",
    "bottom-up": "Bottom-up",
    "seamless": "Seamless",
    "seamed": "Seamed",
    "join as you go": "Join-as-you-go",
    "c2c": "C2C",
    "corner to corner": "C2C",
    "colorwork": "Colorwork",
    "fair isle": "Fair Isle",
    "stranded": "Stranded colorwork",
    "intarsia": "Intarsia",
    "brioche": "Brioche",
    "mosaic": "Mosaic",
    "tapestry": "Tapestry crochet",
    "filet": "Filet crochet",
    "overlay": "Overlay crochet",
    "entrelac": "Entrelac",
    "chart": "Charted",
}


def extract_techniques(p: Dict[str, Any]) -> List[str]:
    out = set()

    # 1) Attributes mapping by permalink/name
    attrs = p.get("pattern_attributes")
    if isinstance(attrs, list):
        for a in attrs:
            if isinstance(a, dict):
                slug = (a.get("permalink") or "").strip().lower()
                nm = (a.get("name") or "").strip().lower()
                lbl = None
                if slug in TECHNIQUE_ATTRS:
                    lbl = TECHNIQUE_ATTRS[slug]
                elif nm in TECHNIQUE_ATTRS:
                    lbl = TECHNIQUE_ATTRS[nm]
                if lbl:
                    out.add(lbl)

    # 2) Keyword scan
    hay = " ".join([
        str(p.get("name") or ""),
        str(p.get("notes") or ""),
        str(p.get("notes_html") or ""),
        str(p.get("gauge_description") or ""),
    ]).lower()

    for kw, label in TECHNIQUE_KEYWORDS.items():
        if kw in hay:
            out.add(label)

    return sorted(out)


# ---------------------------
# Hook/needle size extraction
# ---------------------------
US_HOOK_MM = {
    "B-1": 2.25, "C-2": 2.75, "D-3": 3.25, "E-4": 3.5, "F-5": 3.75,
    "G-6": 4.0,  # note: some brands label G as 4.25mm; we default to 4.0mm
    "7": 4.5, "H-8": 5.0, "I-9": 5.5, "J-10": 6.0, "K-10.5": 6.5,
    "L-11": 8.0, "M/N-13": 9.0, "N/P-15": 10.0, "P": 15.0, "Q": 16.0, "S": 19.0,
}
US_LETTER_BASE = {
    "B": 2.25, "C": 2.75, "D": 3.25, "E": 3.5, "F": 3.75,
    "G": 4.0, "H": 5.0, "I": 5.5, "J": 6.0, "K": 6.5, "L": 8.0, "M": 9.0, "N": 10.0,
    "P": 15.0, "Q": 16.0, "S": 19.0
}


def _parse_metric_mm(value: Any) -> Optional[float]:
    if value is None:
        return None
    s = str(value).lower().replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*mm", s)
    try:
        if m:
            return float(m.group(1))
        if re.fullmatch(r"\d+(?:\.\d+)?", s):
            return float(s)
    except ValueError:
        return None
    return None


def _us_to_mm(us_str: str) -> Optional[float]:
    if not us_str:
        return None
    s = us_str.strip().upper()
    if s in US_HOOK_MM:
        return US_HOOK_MM[s]
    s2 = s.replace("US", "").replace(" ", "").replace("–", "-").replace("—", "-")
    if s2 in US_HOOK_MM:
        return US_HOOK_MM[s2]
    s3 = re.sub(r"[^A-Z]", "", s2)
    if s3 in US_LETTER_BASE:
        return US_LETTER_BASE[s3]
    num = re.sub(r"[^\d.]", "", s)
    if num in US_HOOK_MM:
        return US_HOOK_MM[num]
    return None


def extract_sizes_mm(p: Dict[str, Any]) -> Tuple[List[float], List[float]]:
    needles_mm: List[float] = []
    hooks_mm: List[float] = []
    pns = p.get("pattern_needle_sizes")

    def consume_item(item: Any):
        nonlocal needles_mm, hooks_mm
        if not isinstance(item, dict):
            return
        metric = None
        for key in ("metric", "mm", "metric_size"):
            metric = metric or _parse_metric_mm(item.get(key))
        metric = metric or _parse_metric_mm(item.get("name"))
        us_val = item.get("us") or item.get("name")
        mm = metric or _us_to_mm(str(us_val) if us_val else "")
        if mm is None:
            return
        mm = round(float(mm), 2)
        is_crochet = bool(item.get("crochet")) or ("hook" in str(item.get("name") or "").lower())
        is_knitting = bool(item.get("knitting"))
        if is_crochet and not is_knitting:
            hooks_mm.append(mm)
        elif is_knitting and not is_crochet:
            needles_mm.append(mm)
        else:
            craft = (extract_fiber_art(p) or "").lower()
            if "crochet" in craft:
                hooks_mm.append(mm)
            else:
                needles_mm.append(mm)

    if isinstance(pns, list):
        for item in pns:
            consume_item(item)

    # Fallback: parse gauge_description / gauge
    if not hooks_mm and not needles_mm:
        gd = (p.get("gauge_description") or "") + " " + (p.get("gauge") or "")
        for m in re.findall(r"(\d+(?:\.\d+)?)\s*mm", gd.lower()):
            try:
                val = round(float(m), 2)
            except ValueError:
                continue
            if "crochet" in (extract_fiber_art(p) or "").lower():
                hooks_mm.append(val)
            else:
                needles_mm.append(val)

    return sorted(set(hooks_mm)), sorted(set(needles_mm))


# ---------------------------
# Yarn/materials (fiber-aware)
# ---------------------------
def collect_yarn_ids_and_names(p: Dict[str, Any]) -> Tuple[List[int], List[str]]:
    """
    Collect yarn IDs (for fetching fibers) and yarn names (for fallback materials).
    """
    ids = set()
    yarn_names: List[str] = []
    for pack in p.get("packs") or []:
        yid = pack.get("yarn_id") or (pack.get("yarn") or {}).get("id")
        if isinstance(yid, int):
            ids.add(yid)
        y = pack.get("yarn") or {}
        if y.get("name"):
            yarn_names.append(str(y.get("name")).strip())
        elif pack.get("yarn_name"):
            yarn_names.append(str(pack.get("yarn_name")).strip())
    # Optional: pattern-level yarns, if present
    for y in p.get("yarns") or []:
        if isinstance(y, dict):
            if isinstance(y.get("id"), int):
                ids.add(y["id"])
            if y.get("name"):
                yarn_names.append(str(y["name"]).strip())
    return list(ids), sorted({n for n in yarn_names if n})


def fetch_yarn_details(yarn_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Fetch yarns and make a best-effort to include fiber composition.
    Try both '?include=fibers' and plain endpoint; tolerate transient failures.
    """
    details: List[Dict[str, Any]] = []
    for yid in yarn_ids:
        ok = False
        for url in (
            f"{BASE}/yarns/{yid}.json?include=fibers",
            f"{BASE}/yarns/{yid}.json",
        ):
            try:
                r = requests.get(url, auth=AUTH, timeout=YARN_TIMEOUT)
            except requests.RequestException as e:
                print(f"[WARN] yarn exception for id {yid}: {e}")
                break
            if r.status_code == 200:
                y = r.json().get("yarn") or r.json()
                details.append(y)
                ok = True
                break
            else:
                # try the next URL variant
                continue
        if not ok:
            print(f"[WARN] yarn failed for id {yid}: could not fetch")
        time.sleep(PAUSE_YARN)
    return details


def _iter_fiber_records(yarn_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return a flat list of fiber records from a yarn object, being tolerant to
    different shapes ('fibers', 'yarn_fibers', or nested dicts).
    Expected item shapes handled:
      - {'name': 'Wool', 'pct': 80}
      - {'fiber': {'name': 'Wool'}, 'pct': 80}
      - {'percentage': 80, 'name': 'Wool'}
    """
    fibers = yarn_obj.get("fibers")
    if not fibers:
        fibers = yarn_obj.get("yarn_fibers")
    if not fibers:
        fibers = []

    flat = []
    for f in fibers:
        if not isinstance(f, dict):
            continue
        # possible locations for the fiber name
        name = f.get("name")
        if not name and isinstance(f.get("fiber"), dict):
            name = f["fiber"].get("name")
        if not name and isinstance(f.get("type"), dict):
            name = f["type"].get("name")
        # percentage fields
        pct = f.get("pct")
        if pct is None:
            pct = f.get("percentage", f.get("percent"))
        if name:
            flat.append({"name": str(name).strip(), "pct": pct})
    return flat


def extract_materials_from_yarns(yarns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combine fiber composition across all yarns used in the pattern.
    If pct values exist, normalize to 100 across all yarns combined.
    If no pct values are available anywhere, return unique fiber names with pct=None.
    """
    tally = defaultdict(float)
    names_only = set()

    for y in yarns:
        for f in _iter_fiber_records(y):
            name = f["name"]
            pct = f["pct"]
            if pct is None:
                names_only.add(name)
                continue
            try:
                tally[name] += float(pct)
            except Exception:
                names_only.add(name)

    out: List[Dict[str, Any]] = []
    total = sum(tally.values())

    if total > 0:
        # Normalize the accumulated pct to 100 across all yarns combined
        for name, val in sorted(tally.items(), key=lambda kv: -kv[1]):
            out.append({"fiber": name, "pct": round(100.0 * val / total, 1)})
        # Add unknowns (names without pct) at the end
        for n in sorted(names_only):
            if n not in {m["fiber"] for m in out}:
                out.append({"fiber": n, "pct": None})
    else:
        # No percentages at all anywhere -> just unique names
        for n in sorted(names_only):
            out.append({"fiber": n, "pct": None})

    return out


# ---------------------------
# Designer & URLs
# ---------------------------
def extract_designer_name(p: Dict[str, Any]) -> Optional[str]:
    pa = p.get("pattern_author")
    if isinstance(pa, dict):
        return pa.get("name") or pa.get("username")
    if isinstance(pa, list) and pa:
        return (pa[0] or {}).get("name") or (pa[0] or {}).get("username")
    designers = p.get("designers")
    if isinstance(designers, list) and designers:
        return (designers[0] or {}).get("name")
    d = p.get("designer")
    if isinstance(d, dict):
        return d.get("name")
    if isinstance(d, str):
        return d
    return None


def canonical_ravelry_url(permalink: Optional[str]) -> Optional[str]:
    if not permalink:
        return None
    return f"https://www.ravelry.com/patterns/library/{permalink}"


# ---------------------------
# I/O helpers
# ---------------------------
def save_json(obj: Dict[str, Any], slug: str) -> pathlib.Path:
    path = OUT_DIR / f"{slug}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


def append_csv(rows: List[Dict[str, Any]]) -> None:
    flat = []
    for r in rows:
        rr = dict(r)
        mats = rr.pop("materials", [])
        rr["materials"] = "; ".join(f"{m['fiber']}:{m.get('pct','')}" for m in mats)
        for key in ("stitches_used", "techniques_used", "hook_sizes_mm", "needle_sizes_mm"):
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


# ---------------------------
# Main
# ---------------------------
def main():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] {INPUT_FILE} not found.")
        return

    pairs = read_ids_file(INPUT_FILE)
    print(f"[INFO] Loaded {len(pairs)} patterns from {INPUT_FILE}")

    output_rows: List[Dict[str, Any]] = []
    for i, (pid, fallback_permalink) in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] Fetching ID {pid} ({fallback_permalink})")
        p = fetch_pattern_details(pid)
        time.sleep(PAUSE_DETAIL)
        if not p:
            continue

        permalink = p.get("permalink") or fallback_permalink
        project_type = extract_project_type(p)
        fiber_art = extract_fiber_art(p)
        yarn_weight = extract_weight(p)
        stitches_used = extract_stitches(p)
        techniques_used = extract_techniques(p)
        hook_sizes_mm, needle_sizes_mm = extract_sizes_mm(p)

        yarn_ids, yarn_names = collect_yarn_ids_and_names(p)
        yarns = fetch_yarn_details(yarn_ids) if yarn_ids else []
        materials = extract_materials_from_yarns(yarns)

        # Fallback: if we couldn't derive fibers, at least list yarn names
        if not materials and yarn_names:
            materials = [{"fiber": name, "pct": None} for name in yarn_names]

        ravelry_url = canonical_ravelry_url(permalink)
        external_url = p.get("url")  # often off-Ravelry source (may be empty)
        dload = p.get("download_location") or {}
        free_ravelry_download = bool(p.get("ravelry_download")) and bool(dload.get("free"))
        download_url = dload.get("url")

        enriched = {
            "id": pid,
            "name": p.get("name"),
            "permalink": permalink,
            "url": ravelry_url,
            "external_url": external_url,
            "designer_name": extract_designer_name(p),
            "project_type": project_type,
            "fiber_art": fiber_art,
            "yarn_weight": yarn_weight,
            "materials": materials,
            "stitches_used": stitches_used,
            "techniques_used": techniques_used,   # NEW
            "hook_sizes_mm": hook_sizes_mm,
            "needle_sizes_mm": needle_sizes_mm,
            "published": p.get("published"),
            "sizes_available": p.get("sizes_available"),
            "rating_average": p.get("rating_average"),
            "rating_count": p.get("rating_count"),
            "difficulty_average": p.get("difficulty_average"),
            "favorites_count": p.get("favorites_count"),
            "projects_count": p.get("projects_count"),
            # New flags:
            "free_ravelry_download": free_ravelry_download,
            "download_url": download_url,
        }

        slug = permalink or f"pattern_{pid}"
        save_json(enriched, slug)
        output_rows.append(enriched)

    if output_rows:
        append_csv(output_rows)
        print(f"[INFO] Wrote {len(output_rows)} records to {CSV_PATH}")
    else:
        print("[INFO] No records written.")


if __name__ == "__main__":
    main()
