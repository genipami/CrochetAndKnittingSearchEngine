import faiss
from sentence_transformers import SentenceTransformer
import torch 
import json
import pathlib
from spellchecker import SpellChecker
import csv
from clean_and_chunk import clean_text
from dictionaries import CUSTOM_WORDS, QUERY_SETS

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

def create_chunk_dict() -> dict:
    chunk_dict:dict = {}
    with open("chunks_index.txt", "r", encoding="utf-8") as f:
        chunks = f.read().splitlines()

        for i, chunk in enumerate(chunks, start=0):
            chunk_json = json.loads(chunk)
            chunk_dict[i] = chunk_json["id"]
    return chunk_dict


chunk_dict = create_chunk_dict()

def query_and_print(initial_query:str, top_k:int = 5):
    spell_corrected_query = " ".join(spell.correction(w) for w in initial_query.split())
    query = clean_text(spell_corrected_query)

    scores, idxs = search_in_index(query, top_k)


    for rank, (score, idx) in enumerate(zip(scores, idxs), 1):
        pattern_id = chunk_dict[idx]
        
        files = list(METADATA_DIR.glob(f"{pattern_id}.json"))
        pattern_link = None

        if files:
            with open(files[0], "r", encoding="utf-8") as jf:
                pattern_link = json.load(jf).get("url")
        else:
            pattern_link = "PDF only!"        

        print(rank, score, pattern_id, pattern_link)
def get_int(prompt, *, min_value=None, max_value=None):
    """
    Prompt for an integer with optional min/max validation.
    Keeps asking until a valid value is entered.
    Handles ValueError, EOFError, and KeyboardInterrupt gracefully.
    """
    while True:
        try:
            raw = input(prompt).strip()
            # Reject empty input explicitly
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
            raise  # Re-raise so caller can decide what to do


def calculate_metrics(query_set, top_k=5, set_number=0):
    results = []

    for query in query_set:
        print(f"\nRunning query: {query}")
        query_and_print(query, top_k)

        try:
            pr = get_int("How many results are relevant?: ", min_value=0, max_value=top_k)
            rank = get_int("What is the rank of the first relevant result?: ", min_value=1, max_value=top_k)
            lkrt = get_int(
                "On a scale of 1 to 5 with 5 being the highest, how satisfied are you with these results?: ",
                min_value=1, max_value=5
            )

        except (EOFError, KeyboardInterrupt):
            print("Exiting without saving inputs.")

        precision = pr
        mrr = 0 if rank == 0 else 1 / rank
        likert = lkrt

        with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([set_number, query, top_k, precision, mrr, likert])

        results.append((precision, mrr, likert))

    avg_precision = sum(r[0] for r in results) / len(results)
    avg_mrr = sum(r[1] for r in results) / len(results)
    avg_likert = sum(r[2] for r in results) / len(results)

    print(avg_precision, avg_mrr, avg_likert)
    return avg_precision, avg_mrr, avg_likert

def run_tests():
    results: list = []
    
    for i, query_set in enumerate(QUERY_SETS, start=1):
        (precision_at_5, MRR_at_5, Likert_at_5) = calculate_metrics(query_set, 5)
        (precision_at_10, MRR_at_10, Likert_at_10) = calculate_metrics(query_set, 10)
        results.append([i, 5, precision_at_5, MRR_at_5, Likert_at_5])
        results.append([i, 10, precision_at_10, MRR_at_10, Likert_at_10])
    return results    



def main():
    while True:
        query = input("Search something: ")
        query_and_print(query)

# def main():
#     with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(["Set", "Query", "TopK", "Precision", "MRR", "Likert"])

#     results = run_tests()

#     with open("test_results.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerows(results)


if __name__ == "__main__":
    main()

    