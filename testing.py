import csv
from dictionaries import QUERY_SETS, QUERY_SETS_WITH_FILTERS
from search_engine import FAISS_and_print, hybrid_search
from helpers import get_int
RESULTS_FILE = "all_query_results.csv"

def calculate_metrics(query_set, top_k=5, set_number=0):
    results = []

    for query in query_set:
        print(f"\nRunning query: {query}")
        FAISS_and_print(query, top_k)

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

def calculate_hybrid_metrics(query_set_with_filters, top_k=5, set_number=0):
    results = []
    print("Inside calculate!")
    for qobj in query_set_with_filters:
        query = qobj["query"]
        filters = qobj.get("filters", {}) or {}

        print(f"\nRunning HYBRID query: {query}")
        if filters:
            print(f"Filters: {filters}")

        _ = hybrid_search(
            query,
            filters=filters,
            top_patterns=top_k
        )

        try:
            pr = get_int("How many results are relevant?: ", min_value=0, max_value=top_k)
            rank = get_int("Rank of first relevant result? (0 if none): ", min_value=0, max_value=top_k)
            lkrt = get_int("Satisfaction (1–5)?: ", min_value=1, max_value=5)
        except (EOFError, KeyboardInterrupt):
            print("Exiting without saving inputs for this query.")
            continue

        precision = pr
        mrr = 0 if rank == 0 else 1 / rank
        likert = lkrt

        with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([set_number, query, top_k, precision, mrr, likert])

        results.append((precision, mrr, likert))

    if not results:
        print("No results recorded for this hybrid set.")
        return 0.0, 0.0, 0.0

    avg_precision = sum(r[0] for r in results) / len(results)
    avg_mrr       = sum(r[1] for r in results) / len(results)
    avg_likert    = sum(r[2] for r in results) / len(results)

    print(avg_precision, avg_mrr, avg_likert)
    return avg_precision, avg_mrr, avg_likert

def run_hybrid_tests(QUERY_SETS_WITH_FILTERS):
    print("Inside run tests!")
    results = []

    for i, qset in enumerate(QUERY_SETS_WITH_FILTERS, start=1):
        (p5, m5, l5) = calculate_hybrid_metrics(qset, 5, set_number=i)

        results.append([i, 5, p5, m5, l5])

    return results

def main():
    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Set", "Query", "TopK", "Precision", "MRR", "Likert"])

    results = run_hybrid_tests(QUERY_SETS_WITH_FILTERS)

    with open("test_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(results)

if __name__ == "__main__":
    main()        