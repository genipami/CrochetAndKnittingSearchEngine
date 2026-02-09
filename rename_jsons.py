import json
import pathlib

ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"

def rename_jsons():
    files = sorted(METADATA_DIR.glob("*.json"))
    print(f"[INFO] Found {len(files)} metadata files in {METADATA_DIR}.")

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        pattern_id = data.get("id")
        if not pattern_id:
            print(f"[WARN] Skipping {file.name}: no 'id' field.")
            continue

        new_path = METADATA_DIR / f"{pattern_id}.json"

        if new_path.exists() and new_path != file:
            print(f"[ERROR] Cannot rename {file.name} → {new_path.name}: file already exists.")
            continue

        file.rename(new_path)
        print(f"[OK] {file.name} → {new_path.name}") 

rename_jsons()        