import json
from pathlib import Path
import os
import sys

ROOT_DIR = Path(".").resolve()
CHUNK_DIR = ROOT_DIR / "chunks"

def parse_chunk_filename(filename: str):
    name = filename[:-5]          
    parts = name.split("_")

    pattern_id = int(parts[0])
    source = parts[1]               
    order = int(parts[2])
    return pattern_id, source, order

def build_mappings():
    files = sorted(CHUNK_DIR.glob("*.json"))

    row_meta = {}          
    pattern_to_rows = {}   

    for row_idx, file_path in enumerate(files):
        pattern_id, source, order = parse_chunk_filename(file_path.name)

        row_meta[row_idx] = {
            "pattern_id": pattern_id,
            "source": source,
            "order": order,
            "filename": file_path.name
        }
        pattern_to_rows.setdefault(pattern_id, []).append(row_idx)

    return row_meta, pattern_to_rows

def save_mappings(row_meta, pattern_to_rows):
    with open("row_meta.json", "w", encoding="utf-8") as f:
        json.dump(row_meta, f, indent=2)
    with open("pattern_to_rows.json", "w", encoding="utf-8") as f:
        json.dump(pattern_to_rows, f, indent=2)

def main():
    row_meta, pattern_to_rows = build_mappings()
    save_mappings(row_meta, pattern_to_rows)

if __name__ == "__main__":
    main()    


