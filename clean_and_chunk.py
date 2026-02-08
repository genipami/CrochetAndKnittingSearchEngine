import pathlib
import re
import json
from dictionaries import EQUIV_MAP


ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"
TXT_DIR = ROOT_DIR / "txts"
CHUNK_DIR = ROOT_DIR / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_OVERLAP = 50
CHUNK_SIZE = 500 - CHUNK_OVERLAP


def clean_text(text: str) -> str:
    
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[.,;:!?(){}\[\]\"']", " ", text)

    text = re.sub(r"[\u2010-\u2015\u2018\u2019\u201c\u201d\u2022\u00b7]", " ", text)

    for src, tgt in EQUIV_MAP.items():
        text = re.sub(rf"\b{re.escape(src)}\b", tgt, text)

    text = re.sub(r"\s+", " ", text).strip()

    return text



def chunk_jsons():

    files = sorted(METADATA_DIR.glob("*.json"))
    print(f"[INFO] Found {len(files)} metadata files in {METADATA_DIR}.")

    for i, file in enumerate(files, start=1):
        try:
            js = json.loads(file.read_text(encoding="utf-8", errors="ignore"))
        except Exception as e:
            print(f"[WARN] Could not parse JSON {file.name}: {e}")
            continue

        pattern_id = js.get("id", file.stem)
        notes_raw = js.get("notes") or ""
        notes = clean_text(notes_raw)
        if not notes:
            continue

        words = notes.split()
        n = len(words)

        window = CHUNK_SIZE + CHUNK_OVERLAP
        stride = CHUNK_SIZE if CHUNK_SIZE > 0 else max(1, window)

        num_chunks = max(1, (n + stride - 1) // stride)

        for j in range(num_chunks):
            start = j * stride
            end = min(start + window, n)
            if start >= n:
                break
            chunk_text = " ".join(words[start:end])
            chunk_data = {
                "id" : pattern_id,
                "content" : chunk_text
            }

            chunk_json = json.dumps(chunk_data, indent=4)

            new_path = CHUNK_DIR / f"{pattern_id}_notes_{j+1}.json"
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(chunk_json)

        if i % 500 == 0:
            print(f"[INFO] Processed {i}/{len(files)} files...")

    print("[DONE] Chunking jsons complete.")

def chunk_txts():

    files = sorted(TXT_DIR.glob("*.txt"))
    print(f"[INFO] Found {len(files)} text files in {TXT_DIR}.")

    for i, file in enumerate(files, start=1):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[WARN] Could not parse txt {file.name}: {e}")
            continue

        pattern_id = file.stem
        text = clean_text(text)

        if not text:
            continue

        words = text.split()
        n = len(words)

        window = CHUNK_SIZE + CHUNK_OVERLAP
        stride = CHUNK_SIZE if CHUNK_SIZE > 0 else max(1, window)

        num_chunks = max(1, (n + stride - 1) // stride)

        for j in range(num_chunks):
            start = j * stride
            end = min(start + window, n)
            if start >= n:
                break
            chunk_text = " ".join(words[start:end])
            chunk_data = {
                "id" : pattern_id,
                "content" : chunk_text
            }

            chunk_json = json.dumps(chunk_data, indent=4)

            new_path = CHUNK_DIR / f"{pattern_id}_pattern_{j+1}.json"
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(chunk_json)

        if i % 500 == 0:
            print(f"[INFO] Processed {i}/{len(files)} files...")

    print("[DONE] Chunking txts complete.")
def main():
    chunk_jsons()
    chunk_txts()    

if __name__ == "__main__":
    main()


                








    