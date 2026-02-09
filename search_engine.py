import faiss
from sentence_transformers import SentenceTransformer
import torch 
import json
import pathlib
from spellchecker import SpellChecker
import csv
from clean_and_chunk import clean_text
from dictionaries import CUSTOM_WORDS

spell = SpellChecker()
spell.word_frequency.load_words(CUSTOM_WORDS)

ROOT_DIR = pathlib.Path(".").resolve()
METADATA_DIR = ROOT_DIR / "metadata"

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

        print(rank, score, pattern_id, pattern_link)

def calculate_metrics(query_set, top_k = 5):
    precision_entries:list = []
    MRR_entries:list = []
    Likert_entries:list = []

    for query in query_set:
        query_and_print(query, top_k)
        pr = int(input("How many results are relevant?: "))
        rank = int(input("What is the rank of the first relevant result?: "))
        lkrt = int(input("On a scale of 1 to 5 with 5 being the highest, how satisfied are you with these results?: "))
        precision_entries.append(pr)
        if rank == 0:
            MRR_entries.append(0)
        else:
            MRR_entries.append(1 / rank)
        Likert_entries.append(lkrt)

    precision = sum(precision_entries)/len(precision_entries)
    MRR = sum(MRR_entries)/len(MRR_entries)
    Likert = sum(Likert_entries)/len(Likert_entries)

    return (precision, MRR, Likert)

def run_tests():
    query_sets:list = [
        ["beanie",
        "scarf",
        "shawl",
        "mittens",
        "socks",
        "blanket",
        "cowl",
        "cardigan",
        "vest",
        "poncho",
        "headband",
        "amigurumi",
        "baby hat",
        "crochet bag",
        "knit sweater"],
        ["merino",
        "cotton yarn",
        "acrylic bulky yarn",
        "superwash wool",
        "chenille yarn",
        "velvet yarn",
        "alpaca yarn",
        "worsted weight",
        "dk cotton",
        "fingering wool",
        "super bulky",
        "lightweight cotton hat"],
        ["malabrigo rios",
        "lion brand wool ease",
        "caron simply soft",
        "paintbox dk",
        "scheepjes whirl",
        "katia bambi",
        "bernat velvet",
        "drops paris",
        "drops air",
        "purl soho line weight"],
        ["ribbed",
        "stockinette",
        "garter stitch",
        "brioche",
        "waistcoat stitch",
        "granny square",
        "bobble stitch",
        "puff stitch",
        "cable knit",
        "lace pattern",
        "ribbed brim",
        "colorwork",
        "marling",
        "fade"],
        ["newborn hat",
        "adult size beanie",
        "oversized sweater",
        "easy crochet pattern",
        "intermediate knitting project",
        "top-down raglan",
        "seamless cardigan",
        "quick beginner project",
        "lace shawl intermediate",
        "crochet in the round"],
        ["bulky yarn ribbed beanie",
        "cotton baby blanket crochet",
        "super bulky winter hat",
        "worsted weight cable beanie",
        "dk weight lace shawl",
        "merino fingering colorwork socks",
        "top down raglan sweater knit",
        "crochet velvet scrunchie",
        "half double crochet baby hat",
        "cowl with bobble stitch"],
        ["simple crochet beanie with pompom for beginner",
        "knitted socks with heel flap and gusset in sport yarn",
        "colorwork mitten pattern using worsted wool",
        "crochet amigurumi animal easy pattern",
        "cable knit sweater with raglan shaping top down",
        "warm winter scarf knit in bulky weight merino",
        "baby cardigan with buttons crochet pattern",
        "oversized drop shoulder sweater knit",
        "crochet hat pattern using velvet yarn 0-3 months",
        "knit shawl with fade effect using fingering yarn"],
        ["I'm looking for a quick crochet hat pattern",
        "show me a knitting pattern for a warm chunky scarf",
        "what's a good beginner crochet blanket?",
        "pattern for a cute amigurumi animal",
        "knit sweater for men using worsted yarn",
        "crochet socks pattern for beginners",
        "pattern for a cozy winter hat",
        "I need a lightweight summer shawl",
        "how to crochet a simple beanie",
        "pattern for colorwork mittens"],
        ["crohchet beany",
        "knitted shalw",
        "amigurumy bear",
        "worstd yarn hat",
        "cable knit scraf",
        "chennile scrunchie",
        "bulky yran scarf",
        "merno wool socks",
        "grany sqare",
        "crochet baby hat 0-3 monts"],
        ["top-down seamless yoke sweater in DK merino",
        "toe-up socks with german short row heel",
        "crochet cardigan using moss stitch in aran cotton",
        "laceweight shawl with picot edging",
        "two-color brioche hat",
        "crochet ripple blanket with color changes",
        "knitted balaclava in super bulky yarn",
        "half double crochet earflap hat",
        "cabled fingerless gloves in sport yarn",
        "fair isle beanie knit in the round"]     
    ]

    results: list = []
    
    for i, query_set in enumerate(query_sets, start=1):
        (precision_at_5, MRR_at_5, Likert_at_5) = calculate_metrics(query_set, 5)
        (precision_at_10, MRR_at_10, Likert_at_10) = calculate_metrics(query_set, 10)
        results.append([i, 5, precision_at_5, MRR_at_5, Likert_at_5])
        results.append([i, 10, precision_at_10, MRR_at_10, Likert_at_10])

    return results    



# def main():
#     while True:
#         query = input("Search something: ")
#         query_and_print(query)

def main():
    results = run_tests()
    with open("test_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(results)


if __name__ == "__main__":
    main()

    