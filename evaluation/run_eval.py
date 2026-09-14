"""Evaluation runner for IP-SAKTI RAG retrieval quality.

Scores retrieval (does the right source surface for a question?) against
evaluation/Questions.txt without needing an LLM:

    python evaluation/run_eval.py            # run against a live server
    python evaluation/run_eval.py --local    # run directly against the RAG store

Each line of Questions.txt:
    query | expected_source_keyword | expected_jurisdiction | expected_answer_keyword

Retrieval score: PASS if expected_source_keyword appears in any returned
source name/path. Jurisdiction filtering is also verified when the expected
jurisdiction is not "all".
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

EVAL_FILE = Path(__file__).resolve().parent / "Questions.txt"


def load_cases():
    cases = []
    for raw in EVAL_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            print(f"[EVAL] Skipping malformed line: {line[:60]}...")
            continue
        cases.append({
            "query": parts[0],
            "expected_source": parts[1].lower(),
            "expected_jurisdiction": parts[2].lower(),
            "expected_answer": parts[3].lower(),
        })
    return cases


def sources_from_server(query, jurisdiction, base_url):
    body = json.dumps({"query": query, "jurisdiction": jurisdiction}).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/query",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data.get("sources", []), data.get("confidence"), data.get("answer", "")


def sources_from_local(query, jurisdiction):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from root_search import search_root_data_txt
    from data.rag_loader import RAGStore

    store = RAGStore()
    results = store.query(query, top_k=8, jurisdiction=jurisdiction)
    metadatas = results.get("metadatas", [[]])[0]
    sources = [
        {
            "source": m.get("source", ""),
            "source_path": m.get("source_path", ""),
            "jurisdiction": m.get("jurisdiction", "General"),
        }
        for m in metadatas if m
    ]
    root_hits = search_root_data_txt(query, top_n=3, jurisdiction=jurisdiction)
    if root_hits:
        sources.insert(0, {"source": "data.txt", "source_path": "data.txt", "jurisdiction": "General"})
    return sources, None, ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--local", action="store_true", help="run directly against the RAG store")
    args = parser.parse_args()

    cases = load_cases()
    if not cases:
        print("[EVAL] No cases found.")
        return

    passed = 0
    failures = []
    for case in cases:
        try:
            if args.local:
                sources, _, answer = sources_from_local(case["query"], case["expected_jurisdiction"])
            else:
                sources, _, answer = sources_from_server(case["query"], case["expected_jurisdiction"], args.base_url)
        except Exception as e:
            failures.append((case["query"], f"request failed: {e}"))
            continue

        hay = " ".join(
            (s.get("source", "") + " " + s.get("source_path", "") + " " + s.get("category", "")).lower()
            for s in sources
        )
        ok = case["expected_source"] in hay

        # Jurisdiction check: at least one non-General source must match when a specific jurisdiction is expected
        if ok and case["expected_jurisdiction"] != "all":
            j_ok = any(
                s.get("jurisdiction", "").lower() == case["expected_jurisdiction"]
                for s in sources
            )
            if not j_ok:
                ok = False

        if ok:
            passed += 1
            print(f"PASS  {case['query'][:52]}")
        else:
            src_names = ", ".join(sorted({s.get("source", "?") for s in sources})[:6]) or "none"
            failures.append((case["query"], f"expected source containing '{case['expected_source']}', got: {src_names}"))
            print(f"FAIL  {case['query'][:52]}")

    print()
    print(f"Retrieval score: {passed}/{len(cases)} = {100 * passed / len(cases):.0f}%")
    if failures:
        print("\nFailures:")
        for q, why in failures:
            print(f"  - {q}\n      {why}")


if __name__ == "__main__":
    main()
