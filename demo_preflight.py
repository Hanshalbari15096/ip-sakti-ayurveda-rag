"""Pre-recording demo validation for IP-SAKTI YouTube video.

Run AFTER starting the server (`python app.py`):

    python demo_preflight.py

Checks every endpoint the video demos, prints PASS/FAIL for each,
and caches the exact responses so you know what to expect on camera.
"""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def api(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def check(label, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return ok


def main():
    total = 0
    passed = 0

    print("\n=== IP-SAKTI Demo Preflight ===\n")

    # 1. Health
    print("1. Health check")
    try:
        h = api("GET", "/health")
        total += 1; passed += check("Server running", h.get("status") == "ok")
        total += 1; passed += check("NOT demo mode", not h.get("demo_mode"),
                                    f"demo_mode={h.get('demo_mode')}")
        total += 1; passed += check("RAG docs loaded", h.get("rag_documents", 0) > 0,
                                    f"docs={h.get('rag_documents')}")
    except Exception as e:
        total += 1
        check("Server reachable", False, str(e))
        print("\n  Server not running. Start with: python app.py\n")
        sys.exit(1)

    # 2. Stats
    print("\n2. /stats")
    s = api("GET", "/stats")
    total += 1; passed += check("Has categories", len(s.get("categories", [])) > 0,
                                ", ".join(s.get("categories", [])[:5]))
    total += 1; passed += check("Has jurisdictions", len(s.get("jurisdictions", [])) > 0,
                                ", ".join(s.get("jurisdictions", [])))

    # 3. Languages
    print("\n3. /languages")
    l = api("GET", "/languages")
    total += 1; passed += check("9 languages", len(l.get("languages", [])) >= 9,
                                f"count={len(l.get('languages', []))}")
    total += 1; passed += check("STT provider", l.get("stt_provider") != "Google Speech",
                                f"provider={l.get('stt_provider')}")

    # 4. Corpus version
    print("\n4. /corpus-version")
    cv = api("GET", "/corpus-version")
    total += 1; passed += check("Version info", cv.get("version") != "unknown",
                                f"v={cv.get('version')}")

    # 5. Text query — Demo 2 query
    print("\n5. Text query (Demo 2: patent an Ayurvedic formulation)")
    q = api("POST", "/query", {"query": "How do I patent an Ayurvedic formulation?",
                                "jurisdiction": "india"})
    total += 1; passed += check("Got answer", len(q.get("answer", "")) > 50,
                                f"answer_len={len(q.get('answer', ''))}")
    total += 1; passed += check("Not demo placeholder",
                                "Demo mode" not in q.get("answer", "Demo mode"))
    total += 1; passed += check("Has sources", len(q.get("sources", [])) > 0,
                                f"sources={len(q.get('sources', []))}")
    total += 1; passed += check("Confidence", q.get("confidence") in ("high", "medium"),
                                f"conf={q.get('confidence')}")
    total += 1; passed += check("Has disclaimer", bool(q.get("disclaimer")))

    print(f"\n  Preview answer (first 300 chars):")
    print(f"  {q.get('answer', '')[:300]}")
    print(f"\n  Sources:")
    for src in q.get("sources", [])[:4]:
        print(f"    - {src.get('source')} ({src.get('category')}) "
              f"rel={src.get('relevance_score', '?')}")

    # 6. Formulation classifier questions
    print("\n6. Formulation classifier (/formulation/questions)")
    fq = api("GET", "/formulation/questions")
    total += 1; passed += check("4 steps", len(fq.get("steps", [])) == 4)

    # 7. Formulation classification — Demo 4 path
    print("\n7. Formulation classify (PAM path)")
    fc = api("POST", "/formulation/classify", {"answers": {
        "in_authoritative_text": "no",
        "new_ingredient_or_combination": "yes",
        "standardized_extract": "yes",
        "intended_claims": "treat"
    }})
    total += 1; passed += check("Success", fc.get("success"))
    total += 1; passed += check("Label is PAM",
                                "proprietary" in fc.get("label", "").lower() or
                                "pam" in fc.get("classification", "").lower(),
                                f"label={fc.get('label')}")
    print(f"  Classification: {fc.get('label')}")
    print(f"  Regulatory: {fc.get('regulatory', '')[:100]}")

    # 8. ABS checklist
    print("\n8. ABS checklist")
    ac = api("GET", "/abs/checklist")
    total += 1; passed += check("Has steps", len(ac.get("steps", [])) >= 8,
                                f"steps={len(ac.get('steps', []))}")

    # 9. ABS check — partial completion
    print("\n9. ABS compliance check (partial)")
    ab = api("POST", "/abs/check", {
        "completed": ["identify_resources", "origin_india"],
        "foreign_entity": False,
        "exports": False
    })
    total += 1; passed += check("Not compliant yet", not ab.get("compliant"))
    total += 1; passed += check("Has remaining", len(ab.get("missing_required", [])) > 0,
                                f"remaining={len(ab.get('missing_required', []))}")
    total += 1; passed += check("Percent shown", ab.get("percent_complete", 0) > 0,
                                f"pct={ab.get('percent_complete')}%")

    # 10. Escalation
    print("\n10. Escalation contacts")
    esc = api("GET", "/escalation")
    total += 1; passed += check("6 contacts", len(esc.get("contacts", [])) >= 6,
                                f"count={len(esc.get('contacts', []))}")
    for c in esc.get("contacts", []):
        print(f"    - {c.get('name')}: {c.get('url')}")

    # Summary
    print(f"\n{'='*50}")
    print(f"PREFLIGHT: {passed}/{total} checks passed")
    if passed == total:
        print("ALL CLEAR — ready to record!")
    else:
        print(f"FIX {total - passed} issue(s) before recording.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
