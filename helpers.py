from pathlib import Path
import json
from config import METADATA_DIR
def get_int(prompt, *, min_value=None, max_value=None):

    while True:
        try:
            raw = input(prompt).strip()

            if raw == "":
                print("Please enter a number (input cannot be empty).")
                continue

            value = int(raw)

            if min_value is not None and value < min_value:
                if max_value is not None:
                    print(f"Please enter an integer between {min_value} and {max_value}.")
                else:
                    print(f"Please enter an integer ≥ {min_value}.")
                continue

            if max_value is not None and value > max_value:
                if min_value is not None:
                    print(f"Please enter an integer between {min_value} and {max_value}.")
                else:
                    print(f"Please enter an integer ≤ {max_value}.")
                continue

            return value

        except ValueError:
            print("Invalid input. Please enter a whole number (e.g., 0, 1, 2, ...).")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled by user.")
            raise

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

def get_pattern_info(pattern_id: int) -> dict:
    p = METADATA_DIR / f"{pattern_id}.json"
    return json.load(open(p, "r", encoding="utf-8"))      

def best_chunk_per_pattern(ranked_rows):
    best = {}
    for (row_idx, sim, pattern_id) in ranked_rows:
        if pattern_id is None:
            continue
        if (pattern_id not in best) or (sim > best[pattern_id]["sim"]):
            best[pattern_id] = {"row_idx": row_idx, "sim": sim}

    return sorted(((pid, d["row_idx"], d["sim"]) for pid, d in best.items()), key=lambda x: -x[2])

def parse_float_or_none(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        print("Invalid number, ignoring this filter.")
        return None

def parse_csv_list(s: str):
    return [x.strip().lower() for x in s.split(",") if x.strip()]

def get_filters():
    filters = {}

    fa = input("Filter fiber_art (e.g., crochet/knitting) or blank: ").strip().lower()
    if fa:
        filters["fiber_art"] = fa

    yw = input("Filter yarn_weight (e.g., worsted, super bulky) or blank: ").strip().lower()
    if yw:
        filters["yarn_weight"] = yw

    materials = input("Filter materials (comma-separated fibers, e.g., wool,cotton) or blank: ").strip().lower()
    if materials:
        filters["materials_any"] = parse_csv_list(materials)

    techniques = input("Filter techniques (comma-separated, e.g., raglan,top-down,colorwork) or blank: ").strip().lower()
    if techniques:
        filters["techniques_any"] = parse_csv_list(techniques)

    stitches = input("Filter stitches (comma-separated, e.g., stockinette,garter,rib) or blank: ").strip().lower()
    if stitches:
        filters["stitches_any"] = parse_csv_list(stitches)

    hook_val = parse_float_or_none(input("Filter hook size in mm (single value, e.g., 4.5) or blank: "))
    if hook_val is not None:
        filters["hook_size_mm"] = hook_val

    needle_val = parse_float_or_none(input("Filter needle size in mm (single value, e.g., 4) or blank: "))
    if needle_val is not None:
        filters["needle_size_mm"] = needle_val